class Record:
    def __init__(self, user_id, record_id, date, chat, subject, status, auto, last_save):
        self.record_id = record_id
        self.date = date
        self.chat = chat if chat is not None else []
        self.subject = subject
        self.status = status
        self.auto = auto
        self.user_id = user_id
        self.last_save = last_save


    def load_from_dict(self, data_dict):
        self.record_id = data_dict['record_id']
        self.date = data_dict['date']
        self.chat = data_dict['chat']
        self.subject = data_dict['subject']
        self.status = data_dict['status']
        self.auto = data_dict['auto']


