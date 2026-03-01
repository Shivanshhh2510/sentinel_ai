# app/chat/memory.py

class ChatMemory:

    def __init__(self):
        self.last_column = None
        self.last_action = None

    def update(self, column=None, action=None):
        if column:
            self.last_column = column
        if action:
            self.last_action = action

    def get(self):
        return {
            "column": self.last_column,
            "action": self.last_action
        }


memory = ChatMemory()
