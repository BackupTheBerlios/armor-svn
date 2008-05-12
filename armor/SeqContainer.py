from types import ListType, MethodType

class SeqContainer(object):
    def __init__(self, seq, classes=None, useGenerator=False, **kwargs):
	self.useGenerator = useGenerator
	
	if isinstance(seq, ListType):
	    if self.useGenerator:
		raise TypeError, 'Setting a list to be used as a generator makes no sense!'
	    self.data = seq
	    self.iterator = iter(self.data)

	elif isinstance(seq, MethodType):
	    if useGenerator:
		self.data = seq
		self.iterator = self.data()
	    else:
		self.data = list(seq())
		self.iterator = iter(self.data)

	else:
	    raise TypeError, "List or Generator expected"

	self.classes = classes
	self.__dict__.update(**kwargs)
	

    def __iter__(self):
	return self.iterator
    
    def next(self):
	return self.seq.next()
	
    def reset(self):
	if self.useGenerator:
	    self.iterator = self.data()
	else:
	    self.iterator = iter(self.data)
    
