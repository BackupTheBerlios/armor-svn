import armor.SeqContainer
import armor
import armor.slot

class Prototype(object):
    def __init__(self, slotlist = None):
	self.slots = set(slotlist)
    
    def __getitem__(self, item):
	for i in self.slots:
	    if i.name == item:
		return i
	# Not found
	raise KeyError, "Slot not found"

    def add(self, slot):
	self.slots.add(slot)

	
# class Prototype(object):
#     def __init__(self, inputs = None, outputs = None):
#         self.inContainer = inContainer
        
# class Producer(Prototype):
#     """Prototype class for objects that do not receive any input
#     but provide output (like ImageDataset)."""
#     def __init__(self, inContainer, useGenerator=armor.useGenerator):
#         super(Producer, self).__init__(inContainer)


# class SeqProcessor(Prototype):
#     """Prototype class for objects that receive input and process
#     the data in a sequential order, meaning that each element can
#     be processed independently from the others (e.g. sift and most
#     other feature extractores that work on individual images).
    
#     Lazy evaluation is used by default (armor.useGenerator=Ture) so each
#     element is only processed when it gets accessed."""
#     def __init__(self, inContainer, useGenerator=armor.useGenerator):
#         super(SeqProcessor, self).__init__(inContainer)
#         self.outContainer = armor.SeqContainer.SeqContainer(self.iterator,
# 							    labels=self.inContainer.labels, \
#                                                             owner=self, \
#                                                             classes=self.inContainer.classes, \
#                                                             useGenerator=useGenerator)
        
#     def register(self, reference, group=None):
# 	"""Register to group and propagate further by calling
# 	inContainer.register()."""
#         self.group = group
#         self.inContainer.register(reference, group)

#     def iterator(self, inSlot, processFunc):
# 	"""Generator which iterates over the input elements, calling
# 	funcToCall (must be provided by the inheriting class) and yields
# 	the processed element, one at a time.
# 	"""
#         inputIter = inSlot.container.getIter(group=self.group)
#         for item in inputIter:
# 	    # Convert if necessary
# 	    item = inSlot.convert(item)
#             item = processFunc(item)
#             yield item
            
#         inSlot.container.reset(group=self.group)
        
        
# class BulkProcessor(SeqProcessor):
#     """Prototype class for objects that need all input data present
#     at once (e.g. clustering, normalization). """
#     def iterator(self, slot):
# 	inData = list(self.inputs[slot])

# 	self.inputs[slot].reset()
	
# 	outData = self.process(inData, inLabels)

# 	for item in outData:
# 	    yield item

#     def process(self, data):
# 	return (data)
