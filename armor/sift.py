
from numpy import array,ndarray,float32
import armor.prototypes

class siftObj(armor.prototypes.SeqProcessor):
    def __init__(self, images, useGenerator=True, **kwargs):
        super(siftObj, self).__init__(images, useGenerator)
        self.kwargs = kwargs

    def process(self, img):
	return sift(array(img[0], dtype=float32), **self.kwargs)

        
def sift(*args, **kwargs):
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
