import armor
import armor.slot
import armor.datatypes
from PIL import ImageFilter

class Filter(object):
    def __init__(self, filter=None, useLazyEvaluation=armor.useLazyEvaluation):

	self.filters = {'blur': ImageFilter.BLUR,
			'contour': ImageFilter.CONTOUR,
			'detail': ImageFilter.DETAIL,
			'edge_enhance': ImageFilter.EDGE_ENHANCE,
			'edge_enhance_more': ImageFilter.EDGE_ENHANCE_MORE,
			'emboss': ImageFilter.EMBOSS,
			'find_edges': ImageFilter.FIND_EDGES,
			'sharpen': ImageFilter.SHARPEN,
			'smooth': ImageFilter.SMOOTH,
			'smooth_more': ImageFilter.SMOOTH_MORE}
			   
        self.useLazyEvaluation = useLazyEvaluation

	# Define types
	self.inputType = armor.datatypes.ImageType(format=["PIL"])

	# Define slots
	self.inputSlot = armor.slot.InputSlot(name='Images', acceptsType = self.inputType, useLazyEvaluation=useLazyEvaluation)
	self.outputSlot = armor.slot.OutputSlot(name='Smooted Images',
						inputSlot=self.inputSlot,
						processFunc=armor.weakmethod(self, 'smooth'),
						slotType='sequential',
						useLazyEvaluation=self.useLazyEvaluation)
	self.filter = filter

	
    def smooth(self, img):
	if armor.verbosity > 0:
	    print "Smoothing Image..."
	return img.filter(self.filters[self.filter])

        
