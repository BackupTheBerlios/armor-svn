import armor
import armor.slots
import numpy

class Histogram(object):
    def __init__(self, bins, useLazyEvaluation=armor.useLazyEvaluation):
        self.useLazyEvaluation = useLazyEvaluation
        self.bins = bins
        
        inputType = armor.slots.VectorType(shape=['flatarray'])
        outputType = armor.slots.VectorType(shape='flatarray')

        self.inputSlot = armor.slots.InputSlot(name='vector',
                                               acceptsType=inputType)

        self.outputSlot = armor.slots.OutputSlot(name='histogram',
                                                 inputSlot = self.inputSlot,
                                                 slotType = 'sequential',
                                                 processFunc = armor.weakmethod(self, 'histogram'),
						 outputType = outputType,
                                                 useLazyEvaluation = self.useLazyEvaluation)

        
    def histogram(self, vector):
        if armor.verbosity > 0:
            print "Computing histogram with %i bins..." % self.bins
            if armor.verbosity > 1:
                print numpy.histogram(vector, bins = self.bins, range=(0,self.bins))[0]
        return numpy.histogram(vector, bins = self.bins, range=(0, self.bins))[0]


class Concatenate(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):
        self.useLazyEvaluation = useLazyEvaluation
        
        self.inputType = armor.slots.VectorType(shape=['flatarray'])
        self.outputType = armor.slots.VectorType(shape='flatarray')
        self.inputSlots = []

        self.inputSlot = property(fget=self.__createSlot)
        
        self.outputSlot = armor.slots.OutputSlot(name='concatenated',
                                                 iterator=armor.weakmethod(self, 'concatenate'),
						 outputType=self.outputType,
                                                 useLazyEvaluation = self.useLazyEvaluation)

    def __createSlot(self):
        # For every input we need to have a different inputSlot
        # TODO: check if slot is already registered
	
        inputSlot = armor.slots.InputSlot(name='vector',
                                          acceptsType=self.inputType)

        self.inputSlots.append(inputSlot)

        return inputSlot
        

    def concatenate(self):
        # Pool from every input slot until is StopIteration raised
        output = numpy.array()
        
        try:
            while True:
                for slot in self.inputSlots:
                    # Receive one element
                    output = numpy.concatenate(output, slot.next())

                yield output

        except StopIteration:
            raise StopIteration

        
        
