from AesmaLib.Database import SqliteDB

class Parameter:
    def __init__(self, values=None):
        self.values = [] if values is None else values
        self.last = len(self.values)

    def __str__(self):
        return f"Values: {self.values}"
    
    def __iter__(self):
        for value in self.values:
            yield value
    
    def __next__(self):
        if self.last < len(self.values):
            self.last += 1
            return self.values[self.last]
        else:
            raise StopIteration

    def __add__(self, value):
        self.values.append(value)
        return Parameter(self.values)

    def __sub__(self, value):
        if value in self.values:
            self.values.remove(value)
            return Parameter(self.values)
        else:
            return self


class Info:
    keys = {
        'ID', 'Serial', 'Type', 'Length', 'Stages', 'Shaft'
    }

    def __init__(self, db: SqliteDB=None, rec_id: int=0):
        self.db = db
        self.description = { key: None for key in self.keys }
        if rec_id > 0:
            self.__load(rec_id)

    def set_db(self, db: SqliteDB):
        if db == None:
            print('Pump.Info::', '\terror -> DB = None')
        else:
            self.db = db

    def __load(self, rec_id: int):
        pass

