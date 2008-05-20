import armor.SeqContainer

class Prototype(object):
    def __init__(self, inContainer):
        self.inContainer = inContainer
        self.group = None
        
class Producer(Prototype):
    def __init__(self, inContainer, classes=None, useGenerator=True):
        super(Producer, self).__init__(inContainer)
	
    def register(self, reference, group=None):
        self.group = group

class SeqProcessor(Prototype):
    def __init__(self, inContainer, useGenerator=True):
        super(SeqProcessor, self).__init__(inContainer)
        self.outContainer = armor.SeqContainer.SeqContainer(self.iterator, \
                                                            owner=self, \
                                                            classes = self.inContainer.classes, \
                                                            useGenerator=useGenerator)
        
    def register(self, reference, group=None):
        self.group = group
        self.inContainer.register(reference, group)

    def iterator(self):
        inputIter = self.inContainer.getIter(group=self.group)
        for item in inputIter:
            item = self.postprocess(self.process(self.preprocess(item)))
            yield item
            
        self.inContainer.reset(group=self.group)
        
        
    def preprocess(self, item):
        return item

    def process(self, item):
        return item

    def postprocess(self, item):
        return item
	    

class BulkProcessor(SeqProcessor):

    def iterator(self):
	inData = []
	inLabels = []

	#Split data and labels
	for item in inContainerList:
	    inData.append(item[0])
	    inLabels.append(item[1])
	# Reset the input-iterator
	self.inContainer.reset(group=self.group)
	
	outData = self.process(inData, inLabels)

	for item in outData:
	    yield item

    def process(self, data, labels):
	return (data, labels)
