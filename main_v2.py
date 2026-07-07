import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import re
import time

t_list = []
r_list = []

#Commsignia
def analyze_commsignia(obu_dir, rsu_dir):
    obu_tree = ET.parse(obu_dir)
    rsu_tree = ET.parse(rsu_dir)
    obu_root = obu_tree.getroot()
    rsu_root = rsu_tree.getroot()

    global t_list
    global r_list
    
    #Commsignia-specific: check whether packet was a transmitted or received one
    for packet in obu_root.findall(".//packet"):
        packet_type = None
        c2p_proto = packet.find(".//proto[@name = 'c2p']")
        if c2p_proto is not None:
            match = re.search(r"\bType:\s[TRN][a-z]+\b", c2p_proto.attrib.get("showname"))
            if match:
                if match.group()[6:] == "Transmitted":
                    packet_type = "trans"

        #check SAE J2735 protocol
        j2735_proto = packet.find(".//proto[@name = 'j2735']")
        if j2735_proto is not None and packet_type is not None:
            str = ""
            if j2735_proto.find(".//field[@name = 'j2735.messageId']").attrib.get("show") == "20":
                for field in j2735_proto.iter():
                    field_name = field.attrib.get("name")
                    if re.search(r"[Jj]2735.*\.msgCnt", field_name):
                        str += field.attrib.get("show")
                    if re.search(r"[Jj]2735.*\.secMark", field_name):
                        str += field.attrib.get("show")
            if len(str) != 0:
                if packet_type == "trans":
                    t_list.append(str)


    for packet in rsu_root.findall(".//packet"):
        packet_type = None
        c2p_proto = packet.find(".//proto[@name = 'c2p']")
        if c2p_proto is not None:
            match = re.search(r"\bType:\s[TRN][a-z]+\b", c2p_proto.attrib.get("showname"))
            if match:
                if match.group()[6:] == "Received":
                    packet_type = "rec"

        #check SAE J2735 protocol
        j2735_proto = packet.find(".//proto[@name = 'j2735']")
        if j2735_proto is not None and packet_type is not None:
            str = ""
            if j2735_proto.find(".//field[@name = 'j2735.messageId']").attrib.get("show") == "20":
                for field in j2735_proto.iter():
                    field_name = field.attrib.get("name")
                    if re.search(r"[Jj]2735.*\.msgCnt", field_name):
                        str += field.attrib.get("show")
                    if re.search(r"[Jj]2735.*\.secMark", field_name):
                        str += field.attrib.get("show")
            if len(str) != 0:
                if packet_type == "rec":
                    r_list.append(str)

    t_set = set(t_list)
    r_set = set(r_list)
    for indx, elem in enumerate(t_set):
        if elem in r_set:
            print(f"BSM #{indx + 1} <==> Successfully transmitted\n")
        else:
            print(f"BSM #{indx + 1} <==> Message lost\n")


#Cohda
def analyze_cohda(t_dir, r_dir):
    tx = ET.parse(t_dir)
    rx = ET.parse(r_dir)

    t_root = tx.getroot()
    r_root = rx.getroot()

    global t_list
    global r_list

    #Obtain unique ID of msgCnt concatenated w/ secMark for Rx
    #Append it to the r_list for further analysis
    for r_packet in r_root:
        for r_proto in r_packet:
            if re.search(r"[Jj]2735.*", r_proto.attrib.get("name")): #BSM only appears in SAE J2735 protocol
                str = ""
                for r_field in r_proto.iter():
                    field_name = r_field.attrib.get("name")
                    if re.search(r"[Jj]2735.*\.msgCnt", field_name): #used re to handle old and new PDML files w/ or w/o "_2016"
                        str += r_field.attrib.get("show")
                    if re.search(r"[Jj]2735.*\.secMark", field_name):
                        str += r_field.attrib.get("show")
                if len(str) != 0:
                    r_list.append(str)


    #Same thing as above but for Tx
    for t_packet in t_root:
        for t_proto in t_packet:
            if re.search(r"[Jj]2735.*", t_proto.attrib.get("name")):
                str = ""
                for t_field in t_proto.iter():
                    field_name = t_field.attrib.get("name")
                    if re.search(r"[Jj]2735.*\.msgCnt", field_name):
                        str += t_field.attrib.get("show")
                    if re.search(r"[Jj]2735.*\.secMark", field_name):
                        str += t_field.attrib.get("show")
                if len(str) != 0:
                    t_list.append(str)

    #Change both lists to sets b/c sets have lower time complexities when checking if an elem is present
    t_set = set(t_list)
    r_set = set(r_list)


    # #Export both lists to new txt files
    # with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\t_list.txt", "w") as file:
    #     file.write("\n".join(t_list))

    # with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\r_list.txt", "w") as file:
    #     file.write("\n".join(r_list))

    #Final output document with each BSM analysis printed
    for indx, elem in enumerate(t_set):
        if elem in r_set:
            print(f"BSM #{indx + 1} <==> Successfully transmitted\n")
        else:
            print(f"BSM #{indx + 1} <==> Message lost\n")


def exp_tr_lists():
    with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\t_list.txt", "w") as file:
        file.write("\n".join(t_list))

    with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\r_list.txt", "w") as file:
        file.write("\n".join(r_list))


def cohda_check_files(t_dir, r_dir):
    t_path = Path(t_dir)
    r_path = Path(r_dir)
    t_name = t_path.name
    r_name = r_path.name
    if t_path.suffix != ".pdml" or r_path.suffix != ".pdml": #both have to be PDML files
        return False
    if re.search(r"ts\d", t_name).group()[2] != re.search(r"ts\d", r_name).group()[2]: #check if test nums match
        return False
    if re.search(r"tx", t_name) is None: #Tx (1st arg in main func) should mean transmitted
        return False
    if re.search(r"rx", r_name) is None: #Rx (2nd arg in main func) should mean received
        return False
    if re.search(r"(obu|rsu)\d?-\d", t_name).group()[-1] != re.search(r"(obu|rsu)\d?-\d", t_name).group()[-1]: #check if same dataset num
        return False
    return True
    

def main():
    try:
        t_pdml_dir = sys.argv[1]
        r_pdml_dir = sys.argv[2]
    except IndexError:
        print("Error: Please correctly provide two separate 2 PDML files")
        sys.exit(1)
    inpt_type = None
    # if len(sys.argv) > 2:
    #     inpt_type = "cohda"
    #     t_pdml_dir = sys.argv[1]
    #     r_pdml_dir = sys.argv[2]
    # else:
    #     inpt_type = "comm"
    #     tr_pdml_dir = sys.argv[1]
    
    start_time = time.time()
    # if inpt_type == "cohda":
    #     cohda_check_files(t_pdml_dir, r_pdml_dir)
    #     analyze_cohda(t_pdml_dir, r_pdml_dir)
    analyze_commsignia(t_pdml_dir, r_pdml_dir)
    end_time = time.time()
    print(f"\n\nRun time: {end_time - start_time:.3f} seconds")
    exp_tr_lists()

if __name__ == "__main__":
    main()