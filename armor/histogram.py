import armor
import armor.slot
import armor.datatypes
import numpy

class Histogram(object):
    def __init__(self, bins, useLazyEvaluation=armor.useLazyEvaluation):
	self.useLazyEvaluation = useLazyEvaluation
	self.bins = bins
	
	inputType = armor.datatypes.VectorType(shape=['flatarray'])
	outputType = armor.datatypes.VectorType(shape=['flatarray'])

	self.InputSlot = armor.slot.InputSlot(name='vector',
					      acceptsType=inputType)

	self.OutputSlot = armor.slot.OutputSlot(name='histogram',
						inputSlot = self.InputSlot,
						slotType = 'sequential',
						processFunc = armor.weakmethod(self, 'histogram'),
						useLazyEvaluation = self.useLazyEvaluation)

	
    def histogram(self, vector):
	if armor.verbosity > 0:
	    print "Computing histogram with %i bins..." % self.bins
	return numpy.histogram(vector, bins = self.bins)[0]
