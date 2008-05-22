import armor.SeqContainer
import armor

class Prototype(object):
    def __init__(self, inContainer):
        self.inContainer = inContainer
        self.group = None
        
class Producer(Prototype):
    """Prototype class for objects that do not receive any input
    but provide output (like ImageDataset)."""
    def __init__(self, inContainer, useGenerator=armor.useGenerator):
        super(Producer, self).__init__(inContainer)
	
    def register(self, reference, group=None):
	"""Register to group."""
        self.group = group

class SeqProcessor(Prototype):
    """Prototype class for objects that receive input and process
    the data in a sequential order, meaning that each element can
    be processed independently from the others (e.g. sift and most
    other feature extractores that work on individual images).
    
    Lazy evaluation is used by default (armor.useGenerator=armor.useGenerator) so each
    element is only then processed when it gets accessed."""
    def __init__(self, inContainer, useGenerator=armor.useGenerator):
        super(SeqProcessor, self).__init__(inContainer)
        self.outContainer = armor.SeqContainer.SeqContainer(self.iterator, \
                                                            owner=self, \
                                                            classes=self.inContainer.classes, \
                                                            useGenerator=useGenerator)
        
    def register(self, reference, group=None):
	"""Register to group and propagate further by calling
	inContainer.register()."""
        self.group = group
        self.inContainer.register(reference, group)

    def iterator(self):
	"""Generator which iterates over the input elements, calling
	preprocess(), process() and postprocess() (to be overloaded
	by inheriting class) and yields the processed element, one
	at a time.
	"""
        inputIter = self.inContainer.getIter(group=self.group)
        for item in inputIter:
            item = self.postprocess(self.process(self.preprocess(item)))
            yield item
            
        self.inContainer.reset(group=self.group)
        
        
    def preprocess(self, item):
	"""To be overloaded"""
        return item

    def process(self, item):
	"""To be overloaded"""
        return item

    def postprocess(self, item):
	"""To be overloaded"""
        return item
	    

class BulkProcessor(SeqProcessor):
    """Prototype class for objects that need all input data present
    at once (e.g. clustering, normalization). """
    def iterator(self):
	inData = []
	inLabels = []

	#Split data and labels
	for item in self.inContainer:
	    inData.append(item[0])
	    inLabels.append(item[1])
	# Reset the input-iterator
	self.inContainer.reset(group=self.group)
	
	outData = self.process(inData, inLabels)

	for item in outData:
	    yield item

    def process(self, data, labels):
	return (data, labels)
