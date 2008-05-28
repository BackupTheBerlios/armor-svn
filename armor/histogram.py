import armor
import armor.slot
import armor.datatypes
import numpy

class histogram(object):
    def __init__(self, bins):
	inputType = armor.datatypes.VectorType(shape=['flatarray'])
	outputType = armor.datatypes.VectorType(shape=['flatarray'])

	self.inputSlot = armor.slot.inputSlot(name='vector',
					      acceptsType=inputType)

	self.outputSlot = armor.slot.outputSlot(name='histogram',
						input = self.inputSlot,
						slotType = 'sequential',
						processFunc = self.histogram)

	self.bins = bins


    def histogram(self, vector):
	if armor.verbosity > 0:
	    print "Computing Histogram..."
	return numpy.histogram(vector, bins = self.bins)[0]
