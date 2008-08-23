import armor
import armor.slots
import numpy as np

class Combiner(object):
    """Module that can receive many inputs and stacks them together."""

    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):
        self.inputSlot = armor.slots.MultiInputSlot(name='data')
        self.outputSlot = armor.slots.OutputSlot(name='combined data',
                                                 iterator=armor.weakmethod(self, 'iterator'),
                                                 useLazyEvaluation=useLazyEvaluation)

    def iterator(self):
        # Pool data
        for data in self.inputSlot:
            yield np.concatenate(data)
