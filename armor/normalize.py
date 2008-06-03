from numpy import array,median,std,mean,log,concatenate
from c_types import c_double
import armor
import armor.datatypes
import armor.

class Normalize(object):
    def __init__(self, operation):
	self.operation = operation
	self.inputType = 
    def process(self, data):
	

# The following code was kindly provided by Christoph Lampert
# (christoph.lampert@tuebingen.mpg.de) and comes under the
# Apache-License.

def normalize_data(Xlist, operation=None, operations=None):
    """Normalize data using the specified methods: 'bin'arize, 'L1', 'L2', 'whiten'ing, 
       'bias' (adds 1 to every entry), 'none'
       L1 and L2 are per-sample operations, binarization and whitening are per feature operations"""

    if operation:
	if operations:
	    raise AttributeError, "Specify either operation OR operations"
	operations = [operation]

    Xtmp = []
    for Xi in Xlist:
        Xnorm = array(Xi,c_double)
        for normtype in operations:
            if normtype=='bin':
                Xscale = median(Xnorm) # median is usually better than mean
                Xnorm = 1.*(Xnorm>Xscale)
            elif normtype=='L1':
                Xscale = ascolumn( sum(abs(Xnorm),axis=1) )
                Xscale[Xscale==0]=1.
                Xnorm = Xnorm/Xscale
            elif normtype=='L2':
                Xscale = ascolumn( sqrt(sum(Xnorm**2,axis=1)) )
                Xscale[Xscale==0]=1.
                Xnorm = Xnorm/Xscale
            elif normtype=='whiten':
                Xnorm = Xi-mean(Xnorm,axis=0)
                Xscale = std(Xnorm,axis=0)
                Xscale[Xscale==0]=1.
                Xnorm = Xnorm/Xscale
            elif normtype=='bias':
                Xnorm += 1  # pre-processing to normalization
            elif normtype=='crop':
                crop_thresh=0.1
                Xnorm[Xnorm>crop_thresh] = crop_thresh # pre-processing to normalization
            elif normtype=='log':
                Xnorm = log(Xnorm+1.)
            else:
                pass
        Xtmp.append(Xnorm)
    return array(concatenate(Xtmp,axis=1), c_double) # contiguous array


def ascolumn(X):
    """Reshape data into (n x 1) column vector"""
    return reshape(X, (-1,1))

def asrow(X):
    """Reshape data into (1 x n) row vector"""
    return reshape(X, (1,-1))
