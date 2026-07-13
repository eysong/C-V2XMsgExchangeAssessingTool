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


t_list = []
r_list = []

def analyze_kap(dir, type):
    tree = ET.parse(dir)
    root = tree.getroot()
    global t_list
    global r_list

    ip_device = ""
    #Search for packets transmitted by the OBU
    if type == "trans":
        for packet in root:
            ipv6_proto = packet.find(".//proto[@name = 'ipv6']")
            if ipv6_proto is not None:
                ip_rec = re.search(r"Dst:\s.*", ipv6_proto.attrib.get("showname")).group().replace("Dst: ", "")
                if "ff01" in ip_rec or "ff02" in ip_rec:
                    ip_device = re.search(r"Src:\s.*,", ipv6_proto.attrib.get("showname")).group().replace("Src: ", "")[:-1]
                break
            
        for packet in root:
            packet_type = None
            ipv6_proto = packet.find(".//proto[@name = 'ipv6']")
            if ipv6_proto is not None:
                match = re.search(r"Src:\s.*,", ipv6_proto.attrib.get("showname"))
                if match is not None:
                    if ip_device in match.group():
                        packet_type = "trans"

            j2735_proto = packet.find(".//proto[@name = 'j2735']")
            if j2735_proto is not None and packet_type is not None:
                make_msg_instance(j2735_proto, packet_type)

    elif type == "rec":
        ip_device = ""
        for packet in root:
            ipv6_proto = packet.find(".//proto[@name = 'ipv6']")
            if ipv6_proto is not None:
                ip_rec = re.search(r"Dst:\s.*", ipv6_proto.attrib.get("showname")).group().replace("Dst: ", "")
                if "ff01" in ip_rec or "ff02" in ip_rec:
                    ip_device = re.search(r"Src:\s.*,", ipv6_proto.attrib.get("showname")).group().replace("Src: ", "")[:-1]
                break

        for packet in root:
            packet_type = None
            ipv6_proto = packet.find(".//proto[@name = 'ipv6']")
            if ipv6_proto is not None:
                match = re.search(r"Dst:\s.*", ipv6_proto.attrib.get("showname"))
                if match is not None:
                    if ip_device in match.group():
                        packet_type = "rec"

            j2735_proto = packet.find(".//proto[@name = 'j2735']")
            if j2735_proto is not None and packet_type is not None:
                make_msg_instance(j2735_proto, packet_type)




#Commsignia
def analyze_commsignia(dir, type):
    tree = ET.parse(dir)
    root = tree.getroot()

    global t_list
    global r_list
    
    #Search for packets transmitted by the OBU
    if type == "trans":
        for packet in root:
            packet_type = None
            c2p_proto = packet.find(".//proto[@name = 'c2p']")
            if c2p_proto is not None:
                match = re.search(r"\bType:\s[TRN][a-z]+\b", c2p_proto.attrib.get("showname"))
                if match:
                    if "Transmitted" in match.group():
                        packet_type = "trans"

            #check SAE J2735 protocol
            j2735_proto = packet.find(".//proto[@name = 'j2735']")
            if j2735_proto is not None and packet_type is not None:
                make_msg_instance(j2735_proto, packet_type)


    #Search for packets received by the RSU
    elif type == "rec":
        for packet in root:
            packet_type = None
            c2p_proto = packet.find(".//proto[@name = 'c2p']") #if protocol name is c2p, which is unique to commsignia
            if c2p_proto is not None:
                match = re.search(r"\bType:\s[TRN][a-z]+\b", c2p_proto.attrib.get("showname"))
                if match:
                    if "Received" in match.group():
                        packet_type = "rec"

            #check SAE J2735 protocol
            j2735_proto = packet.find(".//proto[@name = 'j2735']")
            if j2735_proto is not None and packet_type is not None:
                make_msg_instance(j2735_proto, packet_type)


#Cohda
def analyze_cohda(dir, type):
    tree = ET.parse(dir)
    root = tree.getroot()

    global t_list
    global r_list

    if type == "rec":
        packet_type = "rec"
        #Obtain unique ID of msgCnt concatenated w/ secMark for Rx
        #Append it to the r_list for further analysis
        for r_packet in root:
            for r_proto in r_packet:
                if re.search(r"[Jj]2735(_2016)?", r_proto.attrib.get("name")): #BSM only appears in SAE J2735 protocol
                    make_msg_instance(r_proto, packet_type)

    elif type == "trans":
        packet_type = "trans"
        #Same thing as above but for Tx
        for t_packet in root:
            for t_proto in t_packet:
                if re.search(r"[Jj]2735(_2016)?", t_proto.attrib.get("name")):
                    make_msg_instance(t_proto, packet_type)


#--------------------------------------
def build_bsm_id(input_str, msg_cnt, sec_mark, width, length, field, field_name):
    if re.search(r"[Jj]2735(_2016)?\.msgCnt", field_name):
        msg_cnt = field.attrib.get("show")
        input_str += msg_cnt
    if re.search(r"[Jj]2735(_2016)?\.secMark", field_name):
        sec_mark = field.attrib.get("show")
        input_str += sec_mark
    if re.search(r"[Jj]2735(_2016)?\.width", field_name):
        width = field.attrib.get("show")
        input_str += width
    if re.search(r"[Jj]2735(_2016)?\.length", field_name):
        length = field.attrib.get("show")
        input_str += length

    return input_str, msg_cnt, sec_mark, width, length


def build_tim_id(input_str, msg_cnt, lat, long, field, field_name):
    if re.search(r"[Jj]2735(_2016)?\.msgCnt", field_name):
        msg_cnt = field.attrib.get("show")
        input_str += msg_cnt
    if re.search(r"[Jj]2735(_2016)?\.lat", field_name):
        lat = field.attrib.get("show")
        input_str += lat
    if re.search(r"[Jj]2735(_2016)?\.long", field_name):
        long = field.attrib.get("show")
        input_str += long

    return input_str, msg_cnt, lat, long


def build_map_id(input_str, msg_issue_rev, inter, lat, long, field, field_name):
    if re.search(r"[Jj]2735(_2016)?\.msgIssueRevision", field_name):
        msg_issue_rev = field.attrib.get("show")
        input_str += msg_issue_rev
    if re.search(r"[Jj]2735(_2016)?\.intersections", field_name):
        inter = field.attrib.get("show")
        input_str += inter
    if re.search(r"[Jj]2735(_2016)?\.lat(_03)?", field_name): #Note: Old Wireshark exports .lat but new one exports .lat_03, so I used Regex to cover both cases.
        lat = field.attrib.get("show")
        input_str += lat
    if re.search(r"[Jj]2735(_2016)?\.long(_01)?", field_name): #Note: Old Wireshark exports .long but new one exports .long_01, so I used Regex to cover both cases.
        long = field.attrib.get("show")
        input_str += long

    return input_str, msg_issue_rev, inter, lat, long


def build_spat_id(input_str, id, rev, seq_len, field, field_name):
    if re.search(r"[Jj]2735(_2016)?\.id(_01)?", field_name): #Note: Old Wireshark exports .id but new one exports .id_01, so I used Regex to cover both cases.
        id = field.attrib.get("show")
        input_str += id
    if re.search(r"[Jj]2735(_2016)?\.revision", field_name):
        rev = field.attrib.get("show")
        input_str += rev
    if re.search(r"[Jj]2735(_2016)?\.sequence_of_length", field_name):
        seq_len = field.attrib.get("show")
        input_str += seq_len

    return input_str, id, rev, seq_len


#Iterates through the fields in a proto, makes an object based off the message type, and appends it to either t_list or r_list
def make_msg_instance(proto, pack_type):
    combo_id = ""
    field_msg_id = None
    if proto.find(".//field[@name = 'j2735.messageId']") is not None:
        field_msg_id = proto.find(".//field[@name = 'j2735.messageId']")
    elif proto.find(".//field[@name = 'j2735_2016.messageId']") is not None:
        field_msg_id = proto.find(".//field[@name = 'j2735_2016.messageId']")

    if field_msg_id is not None:
        if field_msg_id.attrib.get("show") == "20": #20 = BSM
            msg_cnt = ""
            sec_mark = ""
            width = ""
            length = ""
            for field in proto.iter():
                field_name = field.attrib.get("name")
                combo_id, msg_cnt, sec_mark, width, length = build_bsm_id(combo_id, msg_cnt, sec_mark, width, length, field, field_name)

            if len(combo_id) != 0 and pack_type == "rec":
                r_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))
            elif len(combo_id) != 0 and pack_type == "trans":
                t_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))

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




def final_output():
    # Use Counter, a subclass of dicts
    t_counts = Counter(t_list)  # Key: message object, Value: occurrences
    r_counts = Counter(r_list)

    #Look thru tx msg
    for indx, trans_msg in enumerate(t_counts):
        #A message was successfully received if it exists in the receiver dictionary
        if trans_msg in r_counts:
            if trans_msg.msgType == "BSM":
                print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.msgCnt}, {trans_msg.secMark}, {trans_msg.msgType}, {trans_msg.msgCnt}, {trans_msg.secMark}, {t_counts.get(trans_msg)}, Successfully Received")
            elif trans_msg.msgType == "TIM":
                print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.lat}, {trans_msg.long}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, {t_counts.get(trans_msg)}, Successfully Received")
            elif trans_msg.msgType == "MAP":
                print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.lat}, {trans_msg.long}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, {t_counts.get(trans_msg)}, Successfully Received")
            elif trans_msg.msgType == "SPAT":
                print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.id}, {trans_msg.revision}, {trans_msg.msgType}, {trans_msg.id}, {trans_msg.revision}, {t_counts.get(trans_msg)}, Successfully Received")

        else: #If tx message was not received, then it prints a failed status
            if trans_msg.msgType == "BSM":
                print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.msgCnt}, {trans_msg.secMark}, , , , {t_counts.get(trans_msg)}, Failed to Receive")
            elif trans_msg.msgType == "TIM":
                print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, , , , {t_counts.get(trans_msg)}, Failed to Receive")
            elif trans_msg.msgType == "MAP":
                print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.lat}, {trans_msg.long}, , , , {t_counts.get(trans_msg)}, Failed to Receive")
            elif trans_msg.msgType == "SPAT":
                print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.id}, {trans_msg.revision}, , , , {t_counts.get(trans_msg)}, Failed to Receive")

    #Look thru rx msg
    for indx, rec_msg in enumerate(r_counts):
        #Notes that this message was received from another source is it wasn't found in the tx list
        if rec_msg not in t_counts:
            if rec_msg.msgType == "BSM":
                print(f"#{indx + 1}, , , , {rec_msg.msgType}, {rec_msg.msgCnt}, {rec_msg.secMark}, {t_counts.get(trans_msg)}, Received From Different Source")
            elif rec_msg.msgType == "TIM":
                print(f"#{indx + 1}, , , , {rec_msg.msgType}, {rec_msg.lat}, {rec_msg.long}, {t_counts.get(trans_msg)}, Received From Different Source")
            elif rec_msg.msgType == "MAP":
                print(f"#{indx + 1}, , , , {rec_msg.msgType}, {rec_msg.lat}, {rec_msg.long}, {t_counts.get(trans_msg)}, Received From Different Source")
            elif rec_msg.msgType == "SPAT":
                print(f"#{indx + 1}, , , , {rec_msg.msgType}, {rec_msg.id}, {rec_msg.revision}, {t_counts.get(trans_msg)}, Received From Different Source")




# Export both lists to new txt files
def exp_tr_lists():
    with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\Output Files\t_list.txt", "w") as file:
        file.write("\n".join(msg.comboID for msg in t_list))

    with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\Output Files\r_list.txt", "w") as file:
        file.write("\n".join(msg.comboID for msg in r_list))



#Check if input PDML files for Kapsch are valid
def check_kapsch_file(dir):
    path = Path(dir)
    return check_is_pdml(path) #needs to be .pdml file


#Check if input PDML files for Commsignia are valid
def check_commsignia_file(dir):
    path = Path(dir)
    return check_is_pdml(path) #needs to be .pdml file

#Check if input PDML files for Cohda are valid
def check_cohda_files(t_dir, r_dir):
    t_path = Path(t_dir)
    r_path = Path(r_dir)
    t_name = t_path.name
    r_name = r_path.name
    check_is_pdml(t_path, r_path)
    if re.search(r"ts\d", t_name).group()[2] != re.search(r"ts\d", r_name).group()[2]: #check if test nums match
        return False
    if re.search(r"tx", t_name) is None: #Tx (1st arg in main func) should mean transmitted
        return False
    if re.search(r"rx", r_name) is None: #Rx (2nd arg in main func) should mean received
        return False
    if re.search(r"(obu|rsu)\d?-\d", t_name).group()[-1] != re.search(r"(obu|rsu)\d?-\d", t_name).group()[-1]: #check if same dataset num
        return False
    return True
    

def check_is_pdml(dir):
    if dir.suffix != ".pdml":
        return False

#--------------------------------------

def main():
    try:
        t_inpt_type = sys.argv[1].lower()
        t_pdml_dir = sys.argv[2]
        r_inpt_type = sys.argv[3].lower()
        r_pdml_dir = sys.argv[4]
    except IndexError:
        print("Error: Please follow the described input format.")
        sys.exit(1)
    start_time = time.time()

    if t_inpt_type == "cohda":
        analyze_cohda(t_pdml_dir, "trans")
    elif t_inpt_type == "commsignia":
        analyze_commsignia(t_pdml_dir, "trans")
        if check_commsignia_file == False:
            print("Please provide a valid Commsignia PDML file")
            sys.exit()
    elif t_inpt_type == "kapsch":
        analyze_kap(t_pdml_dir, "trans")
        if check_kapsch_file == False:
            print("Please provide a valid Kapsch PDML file")
            sys.exit()


    if r_inpt_type == "cohda":
        analyze_cohda(r_pdml_dir, "rec")
    elif r_inpt_type == "commsignia":
        analyze_commsignia(r_pdml_dir, "rec")
        if check_commsignia_file == False:
            print("Please provide a valid Commsignia PDML file")
            sys.exit()
    elif r_inpt_type == "kapsch":
        analyze_kap(r_pdml_dir, "rec")
        if check_kapsch_file == False:
            print("Please provide a valid Kapsch PDML file")
            sys.exit()

    final_output()

    end_time = time.time()
    print(f"\n\nRun time: {end_time - start_time:.3f} seconds")
    exp_tr_lists()

if __name__ == "__main__":
    main()