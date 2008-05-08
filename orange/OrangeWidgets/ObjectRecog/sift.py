
from numpy import array,ndarray,float32
import types

class sift:
    def __init__(self, images, **kwargs):
	if type(images) is types.MethodType:
	    self.inputGenerator = images        # Save the generator
	elif type(images) is types.ListType or type(images) is ndarray:
	    self.inputGenerator = None
	    self.images = images

	self.kwargs = kwargs	    
        
        # Generator that yields the descriptors of each single image
	# Structure of one item is: ([descriptors], class)
#        self.iterator = ((self.sift(array(image[0]), **kwargs)[1],image[1]) for image in self.images)

    def iterator(self):
	# self.images can be either a list or a generator
	if self.inputGenerator: 
	    self.images = self.inputGenerator() # Call the generator

	for image in self.images:
	    yield (self.sift(array(image[0], dtype=float32), **self.kwargs)[1],image[1])

	    
    def createDescr(self):
        """Create all the descriptors and save them in self.descriptors"""
        # Generator to List
        self.descriptors = list(self.iterator())

        
    def sift(self, *args, **kwargs):
        """ SIFT  Scale-invariant feature transform
        (F,D) = sift(I) where computes the SIFT frames (keypoints) F and 
        the SIFT descriptors D of the image I. I is a gray-scale image in 
        single precision. Each column of F is a feature frame and has the 
        format [X;Y;S;TH], where X,Y is the (fractional) center of the frame, 
        S is the scale and TH is the orientation (in radians).
        Each column of D is the descriptor of the corresponding frame in F. A
        descriptor is a 128-dimensional vector.
        
        sift(I, option=value, ...) accepts the following options
        
        Octaves
        Set the number of octave of the DoG scale space.
        
        Levels
        Set the number of levels per octave of the DoG scale space.
        
        FirstOctave
        Set the index of the first octave of the DoG scale space.
        
        PeakThresh
        Set the peak selection threshold.
        
        EdgeThresh
        Set the non-edge selection threshold.
        
        NormThresh
        Set the minimum l2-norm of the descriptor before
        normalization. Descriptors below the threshold are set to zero.

        Frames
        Set the frames to use (bypass the detector).
        
        Orientations
        Force the computation of the oritentations of the frames
        even if the option 'Frames' is being used.
        
        Verbose
        Be verbose (may be repeated)."""
        import _sift
        # Type checking, all other type checking is done inside the c function
        assert type(kwargs.get('Octave')) is type(0) or type(kwargs.get('Octave')) is type(None), \
               "'Octave' must be an integer"
        assert type(kwargs.get('Levels')) is type(0) or type(kwargs.get('Levels')) is type(None), \
               "'Levels' must be an integer"
        assert type(kwargs.get('FirstOctave')) is type(0) or type(kwargs.get('FirstOctave')) is type(None), \
               "'FirstOctave' must be an integer"
        assert type(kwargs.get('Orientations')) is type(0) or type(kwargs.get('Orientations')) is type(None), \
               "'Orientations' must be an integer"
        return _sift.sift(*args, **kwargs)
