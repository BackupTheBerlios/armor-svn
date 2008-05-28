import armor
import armor.slot
import armor.datatypes
import numpy
from scipy import cluster

class quantize(object):
    def __init__(self):
        inputTypeVec = armor.datatypes.VectorType(shape=['nestedlist', 'nestedarray'])
        inputTypeCodebook = armor.datatypes.VectorType(name=['codebook'], shape=['flatarray'])
        
        outputType = armor.datatypes.VectorType(shape='flatarray')

        self.inputSlotVec = armor.slot.inputSlot(name='vectors',
                                                 acceptsType=inputTypeVec)

        self.inputSlotCodebook = armor.slot.inputSlot(name='codebook',
                                                      acceptsType=inputTypeCodebook)
        
        self.outputSlot = armor.slot.outputSlot(name='cluster',
                                                outputType=outputType,
                                                iterator=self.quantize,
						inputSlots=[self.inputSlotVec, self.inputSlotCodebook])

    def quantize(self):
        codebook = numpy.array(list(self.inputSlotCodebook))

        for vecs in self.inputSlotVec:
            if armor.verbosity > 0:
                print "Quantizing..."
            clusters = cluster.vq.vq(vecs, codebook)[0]
            yield clusters
                                                