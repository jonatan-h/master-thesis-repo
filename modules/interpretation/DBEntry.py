class DBEntry:
    def __init__(self):
        self.database = {}

    def print_values(self):
        for key in self.database:
            print(key, "->", self.database[key])
