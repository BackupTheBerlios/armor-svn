import armor
import armor.slot
import armor.datatypes
import numpy
from scipy import cluster

class quantize(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):

	self.useLazyEvaluation = useLazyEvaluation

	# Define types
        inputTypeVec = armor.datatypes.VectorType(shape=['nestedlist', 'nestedarray'])
        inputTypeCodebook = armor.datatypes.VectorType(name=['codebook'], shape=['flatarray'])
        
        outputType = armor.datatypes.VectorType(shape='flatarray')

	# Define slots
        self.InputSlotVec = armor.slot.InputSlot(name='vectors',
                                                 acceptsType=inputTypeVec)

        self.InputSlotCodebook = armor.slot.InputSlot(name='codebook',
                                                      acceptsType=inputTypeCodebook)
        
        self.OutputSlot = armor.slot.OutputSlot(name='cluster',
                                                outputType=outputType,
                                                iterator=armor.weakmethod(self, 'quantize'),
						useLazyEvaluation=self.useLazyEvaluation)

    def quantize(self):
	# Get data from codebook slot
        codebook = numpy.array(list(self.InputSlotCodebook))

	# Sequentiall get data from vector slot
        for vecs in self.InputSlotVec:
            if armor.verbosity > 0:
                print "Quantizing..."
            clusters = cluster.vq.vq(vecs, codebook)[0]
            yield clusters
                                                
