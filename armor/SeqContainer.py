from types import ListType, MethodType
import itertools

class SeqContainer(object):
    def __init__(self, seq, owner=None, classes=None, useGenerator=False, **kwargs):
        self.owner = owner
        self.useGenerator = useGenerator
        self.seq = seq
        self.getDataAsIter()
        
        self.classes = classes
        self.__dict__.update(**kwargs)
        self.references = {}
        self.iterpool = {}
        self.iterator = None
	
    def getDataAsIter(self):
        if isinstance(self.seq, ListType):
            if self.useGenerator:
                raise TypeError, 'Setting a list to be used as a generator makes no sense!'
            data = self.seq
            
        elif isinstance(self.seq, MethodType):
            if self.useGenerator:
                data = self.seq()
            else:
		self.seq = list(self.seq())
		data = self.seq

        else:
            raise TypeError, "List or Generator expected"

        return data

    def __iter__(self):
	return self

    def next(self):
	if not self.iterator:
	    self.iterator = iter(self.getDataAsIter())
	for item in self.iterator:
	    yield item
	# Reset:
	self.iterator = iter(self.getDataAsIter())
	
    def reset(self, group=None):
	if not group:
	    self.iterator = None
	
    def register(self, reference, group=None):
	if not self.owner:
	    raise ValueError, 'owner must be set to use this feature'
        self.references[reference] = group
        self.owner.register(self, group=group)

    def getIter(self, group=None):
        if not group:
            return self

        if not self.iterpool.has_key(group) or (self.iterpool.has_key(group) and len(self.iterpool[group]) == 0):
            # How many streams belong to 'group'?
            count = sum((x for x in self.references.values() if x==group))
            self.iterpool[group] = list(itertools.tee(self.getDataAsIter(), count))

        return self.iterpool[group].pop()
