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
    def __init__(self, name, senderSlot=None, group=None, acceptsType=None, bulk=False, useGenerator=armor.useGenerator):
        self.name = name
        self.senderSlot = senderSlot
        self.group = group
        self.acceptsType = acceptsType
        self.container = None
        self.converters = None
	self.bulk = bulk
	self.useGenerator = useGenerator
        
    def __iter__(self):
        if not self.senderSlot:
            raise AttributeError, "No senderSlot registered!"
        return iter(self.container)

    def convertSequential(self):
	for item in self.senderSlot().container:
	    if self.converters is not None:
		if len(self.converters) > 0:
		    for converter in self.converters:
			item = converter(item)
	    yield item

    def convertBulk(self):
	bunch = list(self.senderSlot().container)
	if self.converters is not None:
	    if len(self.converters) > 0:
		for converter in self.converters:
		    bunch = converter(bunch)

	for i in bunch:
	    yield i
	    
    def registerInput(self, senderSlot):
        if armor.useTypeChecking and senderSlot.outputType is not None:
            self.converters = self.acceptsType.compatible(senderSlot.outputType)
            if self.converters == False:
                raise TypeError, "Slots are not compatible"

	if self.senderSlot:
	    if self.senderSlot() is not senderSlot:
		self.senderSlot = weakref.ref(senderSlot)
	
		if armor.useGrouping:
		    senderSlot.container.registerReference(self)
	else:
	    self.senderSlot = weakref.ref(senderSlot)
	    if armor.useGrouping:
		senderSlot.container.registerReference(self)
		
	if not self.bulk:
	    self.container = SeqContainer(generator=self.convertSequential, useGenerator=self.useGenerator)
	else:
	    self.container = SeqContainer(generator=self.convertBulk, useGenerator=self.useGenerator)

        

        
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
	    self.container = SeqContainer(sequence=self.sequence, labels=labels, classes=classes, useGenerator=useGenerator)
	elif self.iterator is not None: # User defined iterator
	    self.container = SeqContainer(generator=self.iterator, labels=labels, classes=classes, useGenerator=useGenerator)
	elif slotType == 'sequential': # Sequential iterator
	    if self.processFunc is None and self.processFuncs is None:
		raise AttributeError, "You must provided processFunc or processFuncs to use generic iterators"
	    self.container = SeqContainer(generator=armor.weakmethod(self, 'seqIterator'), labels=labels, classes=classes, useGenerator=useGenerator)
	elif slotType == 'bulk': # Bulk iterator
    	    if self.processFunc is None and self.processFuncs is None:
		raise AttributeError, "You must provided processFunc or processFuncs to use generic iterators"
	    self.container = SeqContainer(generator=armor.weakmethod(self, 'bulkIterator'), labels=labels, classes=classes, useGenerator=useGenerator)
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
        for item in self.inputSlot.container:
            for processFunc in self.processFuncs:
		if armor.useOrange:
		    from PyQt4.QtGui import qApp
		    qApp.processEvents()
                item = processFunc(item)
            yield item
            

    def bulkIterator(self):
        """Generator which iteratates over the input elements, saves them
        and calls the processFuncs on the complete input data.
        (e.g. clustering, normalization). """
        inData = list(self.inputSlot.container)

        for processFunc in self.processFuncs:
            inData = processFunc(inData)
            
        for item in inData:
            yield item
