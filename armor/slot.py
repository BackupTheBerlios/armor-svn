import armor
from armor.SeqContainer import SeqContainer

class slot(object):
    def __init__(self, name, senderSlot=None, processFunc=None, processFuncs=None, group=None, inputType=None, outputType=None, slotType=None, iterator=None, sequence=None):
        self.name = name
        self.senderSlot = senderSlot
        self.inputType = inputType
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
        inputIter = self.senderSlot.container.getIter(group=self.group)
        for item in inputIter:
            for processFunc in self.processFuncs:
                item = processFunc(item)
            yield item
            
        #self.senderSlot.container.reset(group=self.group)

    def bulkIterator(self):
        """Generator which iteratates over the input elements, saves them
	and calls the processFuncs on the complete input data.
        (e.g. clustering, normalization). """
        inData = list(self.senderSlot.container.getIter(group=self.group))

        #self.senderSlot.container.reset()
        
        for processFunc in self.processFuncs:
            inData = processFunc(inData)
            
        for item in inData:
            yield item
            
    def registerInput(self, senderSlot):
        if armor.useTypeChecking:
            converters = self.inputType.compatible(senderSlot.outputType)
            if converters == False:
                raise TypeError, "Slots are not compatible"
            # Insert them at the beginning of the process cue
            if len(converters) != 0:
                converters.extend(self.processFuncs)
                self.processFuncs = converters
        self.senderSlot = senderSlot

    def registerGroup(self, reference, group=None):
        """Register to group."""
        self.group = group
        # Propagate further
        self.senderSlot.register(group)
    
