import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import re
import time
from V2XMessage import BSM


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
                combo_id = ""
                msg_cnt = ""
                sec_mark = ""
                width = ""
                length = ""
                if j2735_proto.find(".//field[@name = 'j2735.messageId']").attrib.get("show") == "20": #20 = BSM
                    for field in j2735_proto.iter():
                        field_name = field.attrib.get("name")
                        combo_id, msg_cnt, sec_mark, width, length = combo_id_builder(combo_id, msg_cnt, sec_mark, width, length, field, field_name)
                if len(combo_id) != 0 and packet_type == "trans":
                    t_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))

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
                combo_id = ""
                msg_cnt = ""
                sec_mark = ""
                width = ""
                length = ""
                if j2735_proto.find(".//field[@name = 'j2735.messageId']").attrib.get("show") == "20": #20 = BSM
                    for field in j2735_proto.iter():
                        field_name = field.attrib.get("name")
                        combo_id, msg_cnt, sec_mark, width, length = combo_id_builder(combo_id, msg_cnt, sec_mark, width, length, field, field_name)
                if len(combo_id) != 0 and packet_type == "rec":
                    r_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))



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
                combo_id = ""
                msg_cnt = ""
                sec_mark = ""
                width = ""
                length = ""
                if j2735_proto.find(".//field[@name = 'j2735.messageId']").attrib.get("show") == "20": #20 = BSM
                    for field in j2735_proto.iter():
                        field_name = field.attrib.get("name")
                        combo_id, msg_cnt, sec_mark, width, length = combo_id_builder(combo_id, msg_cnt, sec_mark, width, length, field, field_name)
                if len(combo_id) != 0 and packet_type == "trans":
                    t_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))


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
                combo_id = ""
                msg_cnt = ""
                sec_mark = ""
                width = ""
                length = ""
                if j2735_proto.find(".//field[@name = 'j2735.messageId']").attrib.get("show") == "20": #20 = BSM
                    for field in j2735_proto.iter():
                        field_name = field.attrib.get("name")
                        combo_id, msg_cnt, sec_mark, width, length = combo_id_builder(combo_id, msg_cnt, sec_mark, width, length, field, field_name)
                if len(combo_id) != 0 and packet_type == "rec":
                    r_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))



#Cohda
def analyze_cohda(dir, type):
    tree = ET.parse(dir)
    root = tree.getroot()

    global t_list
    global r_list

    if type == "rec":
        #Obtain unique ID of msgCnt concatenated w/ secMark for Rx
        #Append it to the r_list for further analysis
        for r_packet in root:
            for r_proto in r_packet:
                if re.search(r"[Jj]2735(_2016)?", r_proto.attrib.get("name")): #BSM only appears in SAE J2735 protocol
                    combo_id = ""
                    msg_cnt = ""
                    sec_mark = ""
                    width = ""
                    length = ""
                    for r_field in r_proto.iter():
                        field_name = r_field.attrib.get("name")
                        combo_id, msg_cnt, sec_mark, width, length = combo_id_builder(combo_id, msg_cnt, sec_mark, width, length, r_field, field_name)
                    if len(combo_id) != 0:
                        r_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))

    elif type == "trans":
        #Same thing as above but for Tx
        for t_packet in root:
            for t_proto in t_packet:
                if re.search(r"[Jj]2735(_2016)?", t_proto.attrib.get("name")):
                    combo_id = ""
                    msg_cnt = ""
                    sec_mark = ""
                    width = ""
                    length = ""
                    for t_field in t_proto.iter():
                        field_name = t_field.attrib.get("name")
                        combo_id, msg_cnt, sec_mark, width, length = combo_id_builder(combo_id, msg_cnt, sec_mark, width, length, t_field, field_name)
                    if len(combo_id) != 0:
                        t_list.append(BSM(combo_id, msg_cnt, sec_mark, width, length))


#--------------------------------------

def combo_id_builder(input_str, msg_cnt, sec_mark, width, length, field, field_name):
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


def final_output():
    t_set = set(t_list)
    r_set = set(r_list)

    for indx, trans_msg in enumerate(t_set):
        if trans_msg in r_set:
            print(f"#{indx + 1}, {trans_msg.msgType} , {trans_msg.msgCnt}, {trans_msg.secMark}, {trans_msg.msgType}, {trans_msg.msgCnt}, {trans_msg.secMark}, Successfully Transmitted")
        else:
            print(f"#{indx + 1}, {trans_msg.msgType}, {trans_msg.msgCnt}, {trans_msg.secMark}, , , , Failed to Receive")

    for indx, rec_msg in enumerate(r_set):
        if rec_msg not in t_set:
            print(f"#{indx + 1}, , , , {rec_msg.msgType}, {rec_msg.msgCnt}, {rec_msg.secMark}, Received From Different Source")


# Export both lists to new txt files
def exp_tr_lists():
    with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\Output Files\t_list.txt", "w") as file:
        file.write("\n".join(msg.comboID for msg in t_list))

    with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\Output Files\r_list.txt", "w") as file:
        file.write("\n".join(msg.comboID for msg in r_list))


#Check if input PDML files for Commsignia are valid
def commsignia_check_file(dir):
    path = Path(dir)
    return check_is_pdml(path) #needs to be .pdml files

#Check if input PDML files for Cohda are valid
def cohda_check_files(t_dir, r_dir):
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
        t_inpt_type = sys.argv[1]
        t_pdml_dir = sys.argv[2]
        r_inpt_type = sys.argv[3]
        r_pdml_dir = sys.argv[4]
    except IndexError:
        print("Error: Please correctly provide 2 separate PDML files")
        sys.exit(1)
    start_time = time.time()

    if t_inpt_type == "cohda":
        analyze_cohda(t_pdml_dir, "trans")
    elif t_inpt_type == "commsignia":
        analyze_commsignia(t_pdml_dir, "trans")
    elif t_inpt_type == "kap":
        analyze_kap(t_pdml_dir, "trans")

    if r_inpt_type == "cohda":
        analyze_cohda(r_pdml_dir, "rec")
    elif r_inpt_type == "commsignia":
        analyze_commsignia(r_pdml_dir, "rec")
    elif r_inpt_type == "kap":
        analyze_kap(r_pdml_dir, "rec")

    final_output()

    end_time = time.time()
    print(f"\n\nRun time: {end_time - start_time:.3f} seconds")
    exp_tr_lists()

if __name__ == "__main__":
    main()