import armor
import armor.slots
import numpy

class Histogram(object):
    def __init__(self, bins, useLazyEvaluation=armor.useLazyEvaluation):
	self.useLazyEvaluation = useLazyEvaluation
	self.bins = bins
	
	inputType = armor.slots.VectorType(shape=['flatarray'])
	outputType = armor.slots.VectorType(shape=['flatarray'])

	self.inputSlot = armor.slots.InputSlot(name='vector',
                                               acceptsType=inputType)

	self.outputSlot = armor.slots.OutputSlot(name='histogram',
                                                 inputSlot = self.inputSlot,
                                                 slotType = 'sequential',
                                                 processFunc = armor.weakmethod(self, 'histogram'),
                                                 useLazyEvaluation = self.useLazyEvaluation)

	
    def histogram(self, vector):
	if armor.verbosity > 0:
	    print "Computing histogram with %i bins..." % self.bins
            if armor.verbosity > 1:
                print numpy.histogram(vector, bins = self.bins, range=(0,self.bins))[0]
	return numpy.histogram(vector, bins = self.bins, range=(0, self.bins))[0]
