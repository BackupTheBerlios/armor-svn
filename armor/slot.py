import armor
from armor.SeqContainer import SeqContainer

class inputSlot(object):
    def __init__(self, name, senderSlot=None, group=None, acceptsType=None):
        self.name = name
        self.senderSlot = senderSlot
        self.group = group
        self.acceptsType = acceptsType
        self.container = None
        self.converters = None
	
    def __iter__(self):
        if not self.senderSlot:
            raise KeyError, "No senderSlot registered!"
        return iter(self.container)

    def convertInput(self):
        senderIterator = self.senderSlot.container.getIter(self.group)
        for item in senderIterator:
            for converter in self.converters:
                item = converter(item)
            yield item
            
    def registerInput(self, senderSlot):
        if armor.useTypeChecking:
            self.converters = self.acceptsType.compatible(senderSlot.outputType)
            if self.converters == False:
                raise TypeError, "Slots are not compatible"

        self.senderSlot = senderSlot
        self.container = SeqContainer(generator=self.convertInput, slot=self.senderSlot)
        
    def registerGroup(self, reference, group=None):
        """Register to group."""
        self.group = group
        # Propagate further
        self.senderSlot.register(group)

        
class outputSlot(object):
    def __init__(self, name, input=None, processFunc=None, processFuncs=None, group=None, outputType=None, slotType=None, iterator=None, sequence=None):
        self.name = name
        self.inputSlot = input
        self.outputType = outputType
        self.group = group
        self.iterator = iterator
        self.sequence = sequence
        if processFunc:
            if processFuncs:
                raise TypeError, "Specify either processFunc OR processFuncs"
            else:
                self.processFuncs = [processFunc]
        else:
            self.processFuncs = processFuncs

        if not slotType:
            slotType = 'seq'

        # Create an output container
        if self.sequence:
            self.container = SeqContainer(sequence=self.sequence, slot=self)
        elif self.iterator: # User defined iterator
            self.container = SeqContainer(generator=self.iterator, slot=self)
        elif slotType == 'seq': # Sequential iterator
            self.container = SeqContainer(generator=self.seqIterator, slot=self)
        elif slotType == 'bulk': # Bulk iterator
            self.container = SeqContainer(generator=self.bulkIterator, slot=self)

    def __iter__(self):
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
            
        #self.senderSlot.container.reset(group=self.group)

    def bulkIterator(self):
        """Generator which iteratates over the input elements, saves them
        and calls the processFuncs on the complete input data.
        (e.g. clustering, normalization). """
        inData = list(self.inputSlot.container.getIter(group=self.group))

        #self.senderSlot.container.reset()
        
        for processFunc in self.processFuncs:
            inData = processFunc(inData)
            
        for item in inData:
            yield item
            
    def registerGroup(self, reference, group=None):
        """Register to group."""
        self.group = group
        # Propagate further
        self.inputSlot.register(group)
    
