class Demerit:
	def __init__(self, tag,	status, action=None, date=0, notes=""):
		self.tag = tag
		self.action = action
		self.status = status
		self.date = date
		self.notes = notes
