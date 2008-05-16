import armor.SeqContainer

class prototype(object):
    def __init__(self, seqContainer):
        self.seqContainer = seqContainer

    def getData(self, useGenerator=False):
        return armor.SeqContainer.SeqContainer(self.iterator, classes = self.seqContainer.classes, useGenerator=useGenerator)

    def iterator(self):
        for classname,item in self.seqContainer:
            item = self.preprocess(item)
            yield (self.process(item), classname)
        self.seqContainer.reset()
        
    def preprocess(self, item):
        pass

    def process(self, item):
        pass

    def postprocess(self, item):
        pass
