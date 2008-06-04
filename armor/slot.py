import armor
from armor.SeqContainer import SeqContainer
import weakref

class Slots(object):
    """Stores multiple (Input or Output)Slots.
    Each slot can be accessed by its name. Slots['name']."""
    def __init__(self, slots = None):
        self.slots = set(slots)
    
    def __getitem__(self, item):
        for i in self.slots:
            if i.name == item:
                return i
        # Not found
        raise AttributeError, "Slot not found"

    def add(self, slot):
        self.slots.add(slot)
        

class InputSlot(object):
    """Defines an input slot for a module. One output slot can attach
    to an input slot (by calling inputslot.registerInput(senderslot).

    InputSlot(name, senderSlot=None, acceptsType=None,
              bulk=False, useLazyEvaluation=armor.useLazyEvaluation)

    name:         name of the slot, can be any string
    senderSlot:   optional, registers senderSlot
    acceptsType:  optional, a armor.datatype object, if not supplied
                  all types will be accepted.
    bulk:         optional, converts (if necessary) the whole input at
                  once instead of sequentially.
    useLazyEvaluation: optional
    
    """
    def __init__(self, name, senderSlot=None, acceptsType=None, bulk=False, useLazyEvaluation=armor.useLazyEvaluation):
        self.name = name
        self.acceptsType = acceptsType
        self.container = None
        self.converters = None
	self.bulk = bulk
	self.useLazyEvaluation = useLazyEvaluation
	self.senderSlot = None
	self.outputType = None
	
	if senderSlot is not None:
	    self.registerInput(senderSlot)
        
    def __iter__(self):
        if not self.senderSlot:
            raise AttributeError, "No senderSlot registered!"
        return iter(self.container)

    def convertSequential(self):
	for item in self.senderSlot().container:
	    if self.converters is not None: # self.converts contains functions
		if len(self.converters) > 0:
		    for converter in self.converters:
			item = converter(item)
	    yield item

    def convertBulk(self):
	# Get all input data
	bunch = list(self.senderSlot().container)
	# Convert using the functions in self.converters
	if self.converters is not None:
	    if len(self.converters) > 0:
		for converter in self.converters:
		    bunch = converter(bunch)

	for i in bunch:
	    yield i
	    
    def registerInput(self, senderSlot):
        if armor.useTypeChecking and senderSlot.outputType is not None:
	    # Check if sender type is compatible with us or if we can
	    # convert (compatible() will return converter functions)
            compatible = self.acceptsType.compatible(senderSlot.outputType)
            if compatible == False:
                raise TypeError, "Slots are not compatible"
	    # Else compatible() returns the new type and conversion funcs
	    (self.outputType, self.converters) = compatible
	    
	if self.senderSlot:
	    # There is already a senderSlot registered, is it maybe
	    # the same?
	    if self.senderSlot() is not senderSlot:
		# Create a weak reference so that when the senderSlot
		# gets removed this reference wont keep it alive
		self.senderSlot = weakref.ref(senderSlot)
	
		if armor.useCaching:
		    senderSlot.container.registerReference(self)
	else:
	    # Register the new slot
	    self.senderSlot = weakref.ref(senderSlot)
	    if armor.useCaching:
		senderSlot.container.registerReference(self)

	# Initialize the container to store the data (or the reference to it)
	if not self.bulk:
	    self.container = SeqContainer(generator=armor.weakmethod(self, 'convertSequential'), useLazyEvaluation=self.useLazyEvaluation)
	else:
	    self.container = SeqContainer(generator=armor.weakmethod(self, 'convertBulk'), useLazyEvaluation=self.useLazyEvaluation)

        

        
class OutputSlot(object):
    """Defines an output slot which receives data, computes and sends data.
    It is highly configurable. In essence, there are three ways to
    define a valid OutputSlot:
    
    1. provide an inputSlot to read from AND one processFunc (or
    multiple processFuncs) to get called AND a slotType ('sequential'
    or 'bulk') to define if the processFunc(s) should be called for
    each single element from inputSlot (i.e. 'sequential') or if
    processFunc(s) should get called once with all data from
    inputSlot (i.e. 'bulk')

    2. provide an iterator function (you have to specify the input and
    computing yourself) - to be used if you need data from multiple
    inputSlots or if generate data without input.

    3. provide a sequence - can be any iterable.
    """
    def __init__(self, name, inputSlot=None, processFunc=None, processFuncs=None,
		 outputType=None, slotType=None, iterator=None, sequence=None, classes=None,
		 useLazyEvaluation=armor.useLazyEvaluation):

        self.name = name
        self.inputSlot = inputSlot
        self.outputType = outputType
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
	    self.container = SeqContainer(sequence=self.sequence, classes=classes, useLazyEvaluation=useLazyEvaluation)
	elif self.iterator is not None: # User defined iterator
	    self.container = SeqContainer(generator=self.iterator, classes=classes, useLazyEvaluation=useLazyEvaluation)
	elif slotType == 'sequential': # Sequential iterator
	    if self.processFunc is None and self.processFuncs is None:
		raise AttributeError, "You must provide processFunc or processFuncs to use generic iterators"
	    self.container = SeqContainer(generator=armor.weakmethod(self, 'seqIterator'), classes=classes, useLazyEvaluation=useLazyEvaluation)
	elif slotType == 'bulk': # Bulk iterator
    	    if self.processFunc is None and self.processFuncs is None:
		raise AttributeError, "You must provide processFunc or processFuncs to use generic iterators"
	    self.container = SeqContainer(generator=armor.weakmethod(self, 'bulkIterator'), classes=classes, useLazyEvaluation=useLazyEvaluation)
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
