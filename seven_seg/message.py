class Message:
    def __init__(self, string):
        self.string = string

class TimedMessage(Message):
    def __init__(self, string, timeout=2.0):
        super().__init__(string)
        self.timeout = timeout
