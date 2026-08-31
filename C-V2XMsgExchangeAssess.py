import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import re
import time
from V2XMessage import BSM
from V2XMessage import TIM
from V2XMessage import MAP
from V2XMessage import SPAT
from collections import Counter
from datetime import datetime, UTC


t_list = []
r_list = []


# Returns a dict for whichever of input field names are present in the element
def get_field_values(element, field_names):
    result = {}
    for field in element.iter("field"):
        name = field.attrib.get("name")
        if name in field_names and name not in result:
            result[name] = field.attrib.get("show") #updates the name in result dict
    return result


# Determines this device's address by finding its 1st broadcasted packet
def find_device_ip(root):
    for packet in root:
        fields = get_field_values(packet, {"wlan.sa", "wlan.da", "ipv6.src", "ipv6.dst"})

        dst = fields.get("ipv6.dst")
        if dst is not None and ("ff01" in dst or "ff02" in dst): #broadcast dst means this packet's source is the device itself
            return fields.get("ipv6.src"), "ipv6"

        wlan_dst = fields.get("wlan.da")
        if wlan_dst is not None and wlan_dst.lower() == "ff:ff:ff:ff:ff:ff": #wlan broadcast address
            return fields.get("wlan.sa"), "wlan"
    return None, ""


# Finds the SAE J2735 proto layer in a packet, regardless of the dissector version
def find_j2735_proto(packet):
    for proto in packet.iter("proto"):
        name = proto.attrib.get("name")
        if name is not None and re.match(r"j2735(_2016)?$", name):
            return proto
    return None


# Unified analyzer method for all vendors
def analyze_pdml(dir, type):
    tree = ET.parse(dir)
    root = tree.getroot()
    global t_list
    global r_list

    device_ip, proto_type = find_device_ip(root)
    # Packets not sent by this device is something the device received
    addr_field = "wlan.sa" if proto_type == "wlan" else "ipv6.src"

    for packet in root:
        if device_ip is not None:
            addr = get_field_values(packet, {addr_field}).get(addr_field)
            is_from_device = addr is not None and addr.lower() == device_ip.lower()
            if type == "trans" and not is_from_device:
                continue
            if type == "rec" and is_from_device:
                continue

        j2735_proto = find_j2735_proto(packet)
        if j2735_proto is not None:
            make_msg_instance(j2735_proto, type)


# Obtains the needed message attributes
def build_bsm_id(input_str, msg_cnt, sec_mark, width, length, field, field_name):
    if re.search(r"j2735(_2016)?\.msgCnt", field_name):
        msg_cnt = field.attrib.get("show")
        input_str += msg_cnt
    if re.search(r"j2735(_2016)?\.secMark", field_name):
        sec_mark = field.attrib.get("show")
        input_str += sec_mark
    if re.search(r"j2735(_2016)?\.width", field_name):
        width = field.attrib.get("show")
        input_str += width
    if re.search(r"j2735(_2016)?\.length", field_name):
        length = field.attrib.get("show")
        input_str += length

    return input_str, msg_cnt, sec_mark, width, length


def build_tim_id(input_str, msg_cnt, lat, long, field, field_name):
    if re.search(r"j2735(_2016)?\.msgCnt", field_name):
        msg_cnt = field.attrib.get("show")
        input_str += msg_cnt
    if re.search(r"j2735(_2016)?\.lat", field_name):
        lat = field.attrib.get("show")
        input_str += lat
    if re.search(r"j2735(_2016)?\.long", field_name):
        long = field.attrib.get("show")
        input_str += long

    return input_str, msg_cnt, lat, long


def build_map_id(input_str, msg_issue_rev, inter, lat, long, field, field_name):
    if re.search(r"j2735(_2016)?\.msgIssueRevision", field_name):
        msg_issue_rev = field.attrib.get("show")
        input_str += msg_issue_rev
    if re.search(r"j2735(_2016)?\.intersections", field_name):
        inter = field.attrib.get("show")
        input_str += inter
    if re.search(r"j2735(_2016)?\.lat(_03)?", field_name): #Note: Old Wireshark exports .lat but new one exports .lat_03, so I used Regex to cover both cases.
        lat = field.attrib.get("show")
        input_str += lat
    if re.search(r"j2735(_2016)?\.long(_01)?", field_name): #Note: Old Wireshark exports .long but new one exports .long_01, so I used Regex to cover both cases.
        long = field.attrib.get("show")
        input_str += long

    return input_str, msg_issue_rev, inter, lat, long


def build_spat_id(input_str, id, rev, seq_len, field, field_name):
    if re.search(r"j2735(_2016)?\.id(_01)?", field_name): #Note: Old Wireshark exports .id but new one exports .id_01, so I used Regex to cover both cases.
        id = field.attrib.get("show")
        input_str += id
    if re.search(r"j2735(_2016)?\.revision", field_name):
        rev = field.attrib.get("show")
        input_str += rev
    if re.search(r"j2735(_2016)?\.sequence_of_length", field_name):
        seq_len = field.attrib.get("show")
        input_str += seq_len

    return input_str, id, rev, seq_len


# Iterates through the fields in a proto, makes an object based off the message type, and appends it to either t_list or r_list
def make_msg_instance(proto, pack_type):
    combo_id = ""
    field_msg_id = None
    if proto.find(".//field[@name = 'j2735.messageId']") is not None: #New version w/o _2016
        field_msg_id = proto.find(".//field[@name = 'j2735.messageId']")
    elif proto.find(".//field[@name = 'j2735_2016.messageId']") is not None: #Old version w/ _2016
        field_msg_id = proto.find(".//field[@name = 'j2735_2016.messageId']")

    if field_msg_id is not None:
        if field_msg_id.attrib.get("show") == "20": #20 = BSM
            msg_cnt = ""
            sec_mark = ""
            width = ""
            length = ""

            #Old Wireshark exported PDML format
            if proto.find(".//field[@name = 'j2735_2016.lat']") is not None:
                latitude = float(proto.find(".//field[@name = 'j2735_2016.lat']").get("show")) / 10000000.0
            if proto.find(".//field[@name = 'j2735_2016.long']") is not None:
                longitude = float(proto.find(".//field[@name = 'j2735_2016.long']").get("show")) / 10000000.0

            #New Wireshark exported PDML format
            if proto.find(".//field[@name = 'j2735.lat_03']") is not None:
                latitude = float(proto.find(".//field[@name = 'j2735.lat_03']").get("show")) / 10000000.0
            if proto.find(".//field[@name = 'j2735.long_01']") is not None:
                longitude = float(proto.find(".//field[@name = 'j2735.long_01']").get("show")) / 10000000.0

            for field in proto.iter():
                field_name = field.attrib.get("name")
                if field_name is not None:
                    combo_id, msg_cnt, sec_mark, width, length = build_bsm_id(combo_id, msg_cnt, sec_mark, width, length, field, field_name)

            if len(combo_id) != 0 and pack_type == "rec":
                r_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length, latitude, longitude))
            elif len(combo_id) != 0 and pack_type == "trans":
                t_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length, latitude, longitude))

        elif field_msg_id.attrib.get("show") == "31": #31 = TIM
            msg_cnt = ""
            latitude = ""
            longitude = ""
            for field in proto.iter():
                field_name = field.attrib.get("name")
                combo_id, msg_cnt, latitude, longitude = build_tim_id(combo_id, msg_cnt, latitude, longitude, field, field_name)
            if len(combo_id) != 0 and pack_type == "rec":
                r_list.append(TIM(combo_id, msg_cnt, latitude, longitude))
            elif len(combo_id) != 0 and pack_type == "trans":
                t_list.append(TIM(combo_id, msg_cnt, latitude, longitude))
    
        elif field_msg_id.attrib.get("show") == "18": #18 = MAP
            msg_issue_rev = ""
            intersections = ""
            latitude = ""
            longitude = ""
            for field in proto.iter():
                field_name = field.attrib.get("name")
                combo_id, msg_issue_rev, intersections, latitude, longitude = build_map_id(combo_id, msg_issue_rev, intersections, latitude, longitude, field, field_name)
            if len(combo_id) != 0 and pack_type == "rec":
                r_list.append(MAP(combo_id, msg_issue_rev, intersections, latitude, longitude))
            elif len(combo_id) != 0 and pack_type == "trans":
                t_list.append(MAP(combo_id, msg_issue_rev, intersections, latitude, longitude))

        elif field_msg_id.attrib.get("show") == "19": #19 = SPaT
            id = ""
            revision = ""
            sequence_of_length = ""
            for field in proto.iter():
                field_name = field.attrib.get("name")
                combo_id, id, revision, sequence_of_length = build_spat_id(combo_id, id, revision, sequence_of_length, field, field_name)
            if len(combo_id) != 0 and pack_type == "rec":
                r_list.append(SPAT(combo_id, id, revision, sequence_of_length))
            elif len(combo_id) != 0 and pack_type == "trans":
                t_list.append(SPAT(combo_id, id, revision, sequence_of_length))

# Used for Folium map timestamp
def first_bsm_time(dir):
    tree = ET.parse(dir)
    root = tree.getroot()
    for packet in root:
        frame_proto = packet.find(".//proto[@name = 'frame']")
        for field in frame_proto.iter():
            if field.attrib.get("name") == "frame.time_utc":
                return re.sub(r"\..*", "", field.attrib.get("show"))
            else:
                return str(datetime.now(UTC))
                


# Writes results in CSV format
def final_output(dir):
    with open("coords.csv", "w") as file:
        if first_bsm_time(dir) is not None:
            file.write(first_bsm_time(dir)+"\n") #Initiates the timeline of Folium Map
        # Use Counter, a subclass of dicts
        t_counts = Counter(t_list)  # Key: message object, Value: occurrences
        r_counts = Counter(r_list)

        #Look thru tx msg
        for indx, trans_msg in enumerate(t_counts):
            #A message was successfully received if it exists in the receiver dictionary
            if trans_msg in r_counts and trans_msg is not None:
                if trans_msg.msgType == "BSM":
                    print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.msgCnt}, {trans_msg.secMark}, {trans_msg.width}, {trans_msg.length}, {trans_msg.msgType}, {trans_msg.msgCnt}, {trans_msg.secMark}, {trans_msg.width}, {trans_msg.length}, {r_counts.get(trans_msg)}, Successfully Received")
                    file.write(f"{trans_msg.lat}, {trans_msg.long}, True\n")
                elif trans_msg.msgType == "TIM":
                    print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.lat}, {trans_msg.long}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, {r_counts.get(trans_msg)}, Successfully Received")
                    print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, , , , {t_counts.get(trans_msg) - r_counts.get(trans_msg)}, Failed to Receive")
                elif trans_msg.msgType == "MAP":
                    print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.lat}, {trans_msg.long}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, {r_counts.get(trans_msg)}, Successfully Received")
                    print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, , , , {t_counts.get(trans_msg) - r_counts.get(trans_msg)}, Failed to Receive")
                elif trans_msg.msgType == "SPAT":
                    print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.id}, {trans_msg.revision}, {trans_msg.msgType}, {trans_msg.id}, {trans_msg.revision}, {r_counts.get(trans_msg)}, Successfully Received")
                    print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.id}, {trans_msg.revision}, , , , {t_counts.get(trans_msg) - r_counts.get(trans_msg)}, Failed to Receive")

            else: #If tx message was not received, then it prints a failed status
                if trans_msg.msgType == "BSM":
                    print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.msgCnt}, {trans_msg.secMark}, {trans_msg.width}, {trans_msg.length}, , , , , , {r_counts.get(trans_msg)}, Failed to Receive")
                    file.write(f"{trans_msg.lat}, {trans_msg.long}, False\n")
                elif trans_msg.msgType == "TIM":
                    print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, , , , {r_counts.get(trans_msg)}, Failed to Receive")
                elif trans_msg.msgType == "MAP":
                    print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, , , , {r_counts.get(trans_msg)}, Failed to Receive")
                elif trans_msg.msgType == "SPAT":
                    print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.id}, {trans_msg.revision}, , , , {r_counts.get(trans_msg)}, Failed to Receive")


def check_is_pdml(dir):
    path = Path(dir)
    if path.suffix != ".pdml":
        return False
    else:
        return True

#--------------------------------------

def main():
    try:
        t_pdml_dir = sys.argv[1]
        r_pdml_dir = sys.argv[2]
    except IndexError:
        print("Error: Please follow the described input format.")
        sys.exit(1)
    start_time = time.time()

    if check_is_pdml(t_pdml_dir) == False or check_is_pdml(r_pdml_dir) == False:
        print("Please provide PDML files")
        sys.exit(1)

    analyze_pdml(t_pdml_dir, "trans")
    analyze_pdml(r_pdml_dir, "rec")

    final_output(t_pdml_dir)

    end_time = time.time()
    print(f"\n\nRun time: {end_time - start_time:.3f} seconds")

if __name__ == "__main__":
    main()