import armor
import armor.slot
import armor.datatypes
import numpy

class histogram(object):
    def __init__(self, bins, useGenerator=armor.useGenerator):
	self.useGenerator = useGenerator
	self.bins = bins
	
	inputType = armor.datatypes.VectorType(shape=['flatarray'])
	outputType = armor.datatypes.VectorType(shape=['flatarray'])

	self.inputSlot = armor.slot.inputSlot(name='vector',
					      acceptsType=inputType)

	self.outputSlot = armor.slot.outputSlot(name='histogram',
						input = self.inputSlot,
						slotType = 'sequential',
						processFunc = armor.weakmethod(self, 'histogram'),
						useGenerator = self.useGenerator)

	
    def histogram(self, vector):
	if armor.verbosity > 0:
	    print "Computing Histogram with %i bins..." % self.bins
	return numpy.histogram(vector, bins = self.bins)[0]
