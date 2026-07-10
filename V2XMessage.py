class V2XMessage:
    def __init__(self, msg_type):
        self.msgType = msg_type

    def __eq__(self, other):
        # """Defines equality based on the unique combo_id"""
        if type(self) is not type(other):
            return False
        return self.comboID == other.comboID
    
    def __hash__(self):
        # """Allows BSM objects to be stored and compared in sets"""
        return hash(self.comboID)
    

class BSM(V2XMessage):
    def __init__(self, combo_id, msg_cnt, sec_mark, wid, len):
        super().__init__(msg_type = "BSM")
        self.comboID = combo_id
        self.msgCnt = msg_cnt
        self.secMark = sec_mark
        self.width = wid
        self.length = len
    
    def __str__(self):
        return f"BSM with msgCnt: {self.msgCnt} and secMark: {self.secMark}"
    

class TIM(V2XMessage):
    def __init__(self, combo_id, msg_cnt, latitude, longitude):
        super().__init__(msg_type = "TIM")
        self.comboID = combo_id
        self.msgCnt = msg_cnt
        self.lat = latitude
        self.long = longitude

    def __str__(self):
        return f"TIM with msgCnt: {self.msgCnt}, latitude: {self.lat}, and longitude: {self.long}"
    

class MAP(V2XMessage):
    def __init__(self, combo_id, msg_issue_revision, intersections, latitude, longitude):
        super().__init__(msg_type = "MAP")
        self.comboID = combo_id
        self.msgIssueRevision = msg_issue_revision
        self.intersec = intersections
        self.lat = latitude
        self.long = longitude
    
    def __str__(self):
        return f"MAP with issue revision: {self.msgIssueRevision}, intersections: {self.intersec}, latitude: {self.lat}, and longitude: {self.long}"


class SPAT(V2XMessage):
    def __init__(self, combo_id, id, revis, seq_of_len):
        super().__init__(msg_type = "SPAT")
        self.comboID = combo_id
        self.id = id
        self.revision = revis
        self.sequence_of_length = seq_of_len
    
    def __str__(self):
        return f"SPaT with ID: {self.id}, revision: {self.revision}, and sequence of length: {self.sequence_of_length}"