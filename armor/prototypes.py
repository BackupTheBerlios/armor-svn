import armor.SeqContainer

class Prototype(object):
    def __init__(self, inContainer):
        self.inContainer = inContainer
        self.group = None
        
class Producer(Prototype):
    def __init__(self, inContainer, classes=None, useGenerator=True):
        Prototype.__init__(self, inContainer)
        self.outContainer = armor.SeqContainer.SeqContainer(inContainer, \
                                                            owner=self, \
                                                            classes=classes, \
                                                            useGenerator=useGenerator)

    def register(self, reference, group=None):
        self.group = group

class SeqProcessor(Prototype):
    def __init__(self, inContainer, useGenerator=True):
        Prototype.__init__(self, inContainer)
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
	    

