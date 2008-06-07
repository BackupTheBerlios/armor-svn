import armor
import armor.slotss
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
	self.inputSlot = armor.slotss.InputSlot(name='Images', acceptsType = self.inputType, useLazyEvaluation=useLazyEvaluation)
	self.outputSlot = armor.slotss.OutputSlot(name='Filtered Images',
						inputSlot=self.inputSlot,
						processFunc=armor.weakmethod(self, 'applyfilter'),
						slotType='sequential',
						useLazyEvaluation=self.useLazyEvaluation)
	self.filter = filter

	
    def applyfilter(self, img):
	if armor.verbosity > 0:
	    print "Applying filter %s..." % self.filter
	return img.filter(self.filters[self.filter])

        
