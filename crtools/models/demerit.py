class Demerit:
    def __init__(self, tag, status, action=None, date=0, notes=""):
        self.tag = tag.strip()
        self.action = action
        self.status = status
        self.date = date
        self.notes = notes

    def __str__(self):
        return str(self.__dict__)

    def merge(self, other_demerit):
        self.notes = '{}<br>- {}'.format(other_demerit.notes, self.notes)
        if not self.notes.startswith('<br>- '):
            self.notes = '<br>- {}'.format(self.notes)
