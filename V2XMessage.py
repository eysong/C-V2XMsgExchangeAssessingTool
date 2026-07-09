class V2XMessage:
    def __init__(self, msg_type):
        self.msgType = msg_type


class BSM(V2XMessage):
    def __init__(self, combo_id, msg_cnt, sec_mark, wid, len):
        super().__init__(msg_type = "BSM")
        self.comboID = combo_id
        self.msgCnt = msg_cnt
        self.secMark = sec_mark
        self.width = wid
        self.length = len

    # def __eq__(self, other):
    #     # """Defines equality based on the unique combo_id"""
    #     if not isinstance(other, BSM):
    #         return False
    #     return self.comboID == other.comboID
    
    # def __hash__(self):
    #     # """Allows BSM objects to be stored and compared in sets"""
    #     return hash(self.comboID)
    
    def __str__(self):
        return f"BSM({self.comboID})"