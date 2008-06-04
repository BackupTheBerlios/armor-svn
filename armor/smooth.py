import armor
import armor.slot
import armor.datatypes
import PIL.ImageFilter

class Smooth(object):
    def __init__(self, useLazyEvaluation=armor.useLazyEvaluation):

        self.useLazyEvaluation = useLazyEvaluation

	# Define types
	self.inputType = armor.datatypes.ImageType(format=["PIL"])

	# Define slots
	self.inputSlot = armor.slot.InputSlot(name='Images', acceptsType = self.inputType, useLazyEvaluation=useLazyEvaluation)
	self.outputSlot = armor.slot.OutputSlot(name='Smooted Images',
						inputSlot=self.InputSlot,
						processFunc=armor.weakmethod(self, 'smooth'),
						outputType = self.inputSlot.outputType,
						slotType='sequential',
						useLazyEvaluation=self.useLazyEvaluation)

    def smooth(self, img):
	if armor.verbosity > 0:
	    print "Smoothing Image..."
	return img.filter(PIL.ImageFilter.SMOOTH)

        
