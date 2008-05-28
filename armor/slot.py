import armor
from armor.SeqContainer import SeqContainer
import weakref

class slots(object):
    def __init__(self, slotlist = None):
        self.slots = set(slotlist)
    
    def __getitem__(self, item):
        for i in self.slots:
            if i.name == item:
                return i
        # Not found
        raise AttributeError, "Slot not found"

    def add(self, slot):
        self.slots.add(slot)
        

class inputSlot(object):
    def __init__(self, name, senderSlot=None, group=None, acceptsType=None, bulk=False):
        self.name = name
        self.senderSlot = senderSlot
        self.group = group
        self.acceptsType = acceptsType
        self.container = None
        self.converters = None
	self.bulk = bulk
        
    def __iter__(self):
        if not self.senderSlot:
            raise AttributeError, "No senderSlot registered!"
        return iter(self.container)

    def convertSequential(self):
        senderIterator = self.senderSlot.container.getIter(self.group)
	if not self.bulk:
	    for item in senderIterator:
		if self.converters and len(self.converters) > 0:
		    for converter in self.converters:
			item = converter(item)
		yield item

    def convertBulk(self):
	senderIterator = self.senderSlot.container.getIter(self.group)
	bunch = list(senderIterator)
	if self.converters and len(self.converters) > 0:
	    for converter in self.converters:
		bunch = converter(bunch)

	for i in bunch:
	    yield i
	    
    def registerInput(self, senderSlot):
        if armor.useTypeChecking and senderSlot.outputType:
            self.converters = self.acceptsType.compatible(senderSlot.outputType)
            if self.converters == False:
                raise TypeError, "Slots are not compatible"

        self.senderSlot = senderSlot
	if not self.bulk:
	    self.container = SeqContainer(generator=self.convertSequential, slot=self.senderSlot)
	else:
	    self.container = SeqContainer(generator=self.convertBulk, slot=self.senderSlot)
        
    def registerGroup(self, reference=None, group=None):
        """Register to group."""
        self.group = group
        self.container.registerGroup(group=self.group)
        # Propagate further
        self.senderSlot.registerGroup(group=self.group)

        
class outputSlot(object):
    def __init__(self, name, input=None, inputSlots=None, processFunc=None, processFuncs=None, group=None, outputType=None, slotType=None, iterator=None, sequence=None, labels=None, classes=None, useGenerator=armor.useGenerator):
        self.name = name
        self.inputSlot = input
	self.inputSlots = inputSlots
        self.outputType = outputType
        self.group = group
        self.iterator = iterator
        self.sequence = sequence
	self.processFunc = processFunc
	
        if processFunc is not None:
            if processFuncs is not None:
                raise TypeError, "Specify either processFunc OR processFuncs"
            else:
                self.processFuncs = [processFunc]
        else:
            self.processFuncs = processFuncs

        # Create an output container
	if self.sequence is not None:
	    self.container = SeqContainer(sequence=self.sequence, slot=self, labels=labels, classes=classes, useGenerator=useGenerator)
	elif self.iterator is not None: # User defined iterator
	    self.container = SeqContainer(generator=self.iterator, slot=self, labels=labels, classes=classes, useGenerator=useGenerator)
	elif slotType == 'sequential': # Sequential iterator
	    if self.processFunc is None and self.processFuncs is None:
		raise AttributeError, "You must provided processFunc or processFuncs to use generic iterators"
	    self.container = SeqContainer(generator=self.seqIterator, slot=self, labels=labels, classes=classes, useGenerator=useGenerator)
	elif slotType == 'bulk': # Bulk iterator
    	    if self.processFunc is None and self.processFuncs is None:
		raise AttributeError, "You must provided processFunc or processFuncs to use generic iterators"
	    self.container = SeqContainer(generator=self.bulkIterator, slot=self, labels=labels, classes=classes, useGenerator=useGenerator)
	else:
	    self.container = None
	    
    def __iter__(self):
	if not self.container:
	    raise AttributeError, "self.container is not set"
        return iter(self.container)
    
    def seqIterator(self):
        """Generator which iterates over the input elements, calling
        processFuncs and yields the processed element, one at a time.
        """
        inputIter = self.inputSlot.container.getIter(group=self.group)
        for item in inputIter:
            for processFunc in self.processFuncs:
                item = processFunc(item)
            yield item
            

    def bulkIterator(self):
        """Generator which iteratates over the input elements, saves them
        and calls the processFuncs on the complete input data.
        (e.g. clustering, normalization). """
        inData = list(self.inputSlot.container.getIter(group=self.group))

        for processFunc in self.processFuncs:
            inData = processFunc(inData)
            
        for item in inData:
            yield item
            
    def registerGroup(self, reference=None, group=None):
        """Register to group."""
        self.group = group
        self.container.registerGroup(group=self.group)
        # Propagate further
        if self.inputSlot is not None:
            self.inputSlot.registerGroup(group=self.group)
	elif self.inputSlots is not None:
	    for slot in self.inputSlots:
		slot.registerGroup(group=self.group)
    
