class slot(object):
    def __init__(self, name, inputSlot=None, processFunc=None, processFuncs=None, group=None, inputType=None, outputType=None, slotType=None, itertator=None):
	self.name = name
	self.inputSlot = inputSlot
        self.datatype = datatype
        self.group = group
	self.iterator = iterator
	if processFunc:
	    if processFuncs:
		raise TypeError, "Specify either processFunc OR processFuncs"
	    self.processFuncs = [processFunc]
	else:
	    self.processFuncs = processFuncs
	    
	if not slotType:
	    slotType = 'seq'

	# Create an output container
	if self.iterator: # User defined iterator
	    self.container = SeqContainer(self.iterator, slot=self, processFuncs=self.processFuncs)
	eif slotType == 'seq': # Sequential iterator
	    self.container = SeqContainer(self.seqIterator, slot=self, processFuncs=self.processFuncs)
	elif slotType == 'bulk': # Bulk iterator
	    self.container = SeqContainer(self.bulkIterator, slot=self, processFuncs=self.processFuncs)

    def seqIterator(self):
	"""Generator which iterates over the input elements, calling
	funcToCall (must be provided by the inheriting class) and yields
	the processed element, one at a time.
	"""
        inputIter = self.senderSlot.container.getIter(group=self.group)
        for item in inputIter:
	    for processFunc in self.processFuncs:
		item = processFunc(item)
            yield item
            
        self.inputSlot.container.reset(group=self.group)

    def bulkIterator(self):
	inData = list(self.inputSlot.container.getIter(group=self.group))

	self.inputSlot.container.reset()
	
	for processFunc in self.processFuncs:
	    inData = processFunc(inData)
	    
	for item in outData:
	    yield item
	    
    def registerInput(self, inputSlot):
        converters = self.datatype.compatible(inputSlot.datatype)
        if converters == False:
            raise TypeError, "Slots are not compatible"
	# Insert them at the beginning of the process cue
	self.processFuncs = converters.extend(self.processFuncs)
	self.inputSlot = inputSlot

    def registerGroup(self, reference, group=None):
        """Register to group."""
        self.group = group
        # Propagate further
        self.inputSlot.register(group)
    
