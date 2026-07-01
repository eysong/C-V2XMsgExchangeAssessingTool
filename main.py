import xml.etree.ElementTree as ET
import sys
import re

#hard-coded PDML file inpts for now
tx = ET.parse(r"C:\Users\sns123\Documents\C-V2I-testing-datasets-PDML\C-V2I-2024-07-30-ts1-tx-obu1-0.pdml")
rx = ET.parse(r"C:\Users\sns123\Documents\C-V2I-testing-datasets-PDML\C-V2I-2024-07-30-ts1-rx-rsu-0.pdml")

t_root = tx.getroot()
r_root = rx.getroot()

# #test with condensed PDML file
# tree = ET.parse(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\cond_tx_obu.xml")
# root = tree.getroot()

t_list = []
r_list = []

#!!!!!!!!NEED TO MODIFY: SECMARK DOES RESET DUE TO OVERFLOW. MAX IS ~60K!!!!!!!!!!!!
#Before start looping, check the timestamps of the first messages to confirm any losses
# def get_first_msg_time():
#     r_field = r_root.find(".//field[@name='j2735_2016.secMark']")

#     if r_field is not None:
#         return int(r_field.attrib.get("show"))
    
#     return None

# r_firstmsgtime = get_first_msg_time()
# print(r_firstmsgtime)


for r_packet in r_root:
    for r_proto in r_packet:
        str = ""
        for r_field in r_proto.iter():
            if r_field.attrib.get("name") == "j2735_2016.msgCnt":
                str += r_field.attrib.get("show")
            if r_field.attrib.get("name") == "j2735_2016.secMark":
                str += r_field.attrib.get("show")
        if len(str) != 0:
            r_list.append(str)


#Anything in Tx before R_firstmsg will have been known to be lost
#So we skip all Tx messages that come before R_firstmsg
for t_packet in t_root:
    for t_proto in t_packet:
        str = ""
        for t_field in t_proto.iter():
            if t_field.attrib.get("name") == "j2735_2016.msgCnt":
                str += t_field.attrib.get("show")
            if t_field.attrib.get("name") == "j2735_2016.secMark":
                # if int(t_field.attrib.get("show")) >= r_firstmsgtime:
                str += t_field.attrib.get("show")
        if len(str) != 0:
            t_list.append(str)
                



#-------------------
# for t_packet in t_root:
#     for t_proto in t_packet:
#         for t_field in t_proto.iter():
#             if t_field.attrib.get("name") == "j2735_2016.msgCnt":
#                 # if t_field.attrib.get("show") == "45":
#                 #     print("Found it!")
#                 Tmsgcnt = t_field.attrib.get("show")


t_set = set(t_list)
r_set = set(r_list)


#Export both lists to new txt files
with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\t_list.txt", "w") as file:
    file.write("\n".join(t_list))

with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\r_list.txt", "w") as file:
    file.write("\n".join(r_list))

with open(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\results.txt", "w") as file:
    for indx, elem in enumerate(t_set):
        if elem in r_set:
            file.write(f"BSM #{indx} <==> Successfully transmitted\n")
        else:
            file.write(f"BSM #{indx} <==> Message lost\n")

print("done")