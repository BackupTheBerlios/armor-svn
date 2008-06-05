from numpy import array,median,std,mean,log,concatenate,sum,reshape,sqrt
from ctypes import c_double
import armor
import armor.datatypes
import armor.slot

class Normalize(object):
    def __init__(self, normtype, useLazyEvaluation=armor.useLazyEvaluation):
        self.normtype = normtype
        if self.normtype in ['L1','L2']:
            self.sequential = False
        elif self.normtype in ['bin', 'whiten', 'bias', 'crop', 'log']:
            self.sequential = True
        else:
            raise ValueError, "No operation mode specified"

        if self.sequential:
            self.inputType = armor.datatypes.VectorType(shape=['flatarray'])
        else:
            self.inputType = armor.datatypes.VectorType(shape=['flatarray'], bulk=True)

        self.outputType = armor.datatypes.VectorType(shape='flatarray')

        self.inputSlot = armor.slot.InputSlot(name='unnormalized',
                                              acceptsType=self.inputType)
        if self.sequential:
            self.outputSlot = armor.slot.OutputSlot(name='normalized',
                                                    inputSlot=self.inputSlot,
                                                    slotType='sequential',
                                                    processFunc=armor.weakmethod(self, 'normalize_seq'),
                                                    outputType=self.outputType,
						    useLazyEvaluation=useLazyEvaluation)
        else:
            self.outputSlot = armor.slot.OutputSlot(name='normalized',
                                                    inputSlot=self.inputSlot,
                                                    slotType='bulk',
                                                    processFunc=armor.weakmethod(self, 'normalize_bulk'),
                                                    outputType=self.outputType,
						    useLazyEvaluation=useLazyEvaluation)
                                                
            
        

        

    # The following code was kindly provided by Christoph Lampert
    # (christoph.lampert@tuebingen.mpg.de) and comes under the
    # Apache-License.

    def normalize_seq(self, data):
        if armor.verbosity>0:
            print "Normalizing %s..." % self.normtype
        Xnorm = array(data)
        if self.normtype=='bin':
            Xscale = median(Xnorm) # median is usually better than mean
            Xnorm = 1.*(Xnorm>Xscale)
        elif self.normtype=='whiten':
            Xnorm = Xnorm-mean(Xnorm,axis=0)
            Xscale = std(Xnorm,axis=0)
            Xnorm[Xnorm==0.]=1.
            Xnorm = Xnorm/Xscale
        elif self.normtype=='bias':
            Xnorm += 1  # pre-processing to normalization
        elif self.normtype=='crop':
            crop_thresh=0.1
            Xnorm[Xnorm>crop_thresh] = crop_thresh # pre-processing to normalization
        elif self.normtype=='log':
            Xnorm = log(Xnorm+1.)

        return Xnorm

    def normalize_bulk(self, data):
        if armor.verbosity>0:
            print "Normalizing %s..." % self.normtype

        Xnorm = array(data)
        if self.normtype=='L1':
            Xscale = ascolumn( sum(abs(Xnorm),axis=1) )
            Xscale[Xscale==0]=1.
            Xnorm = Xnorm/Xscale
        elif self.normtype=='L2':
            Xscale = ascolumn( sqrt(sum(Xnorm**2,axis=1)) )
            Xscale[Xscale==0]=1.
            Xnorm = Xnorm/Xscale
        return Xnorm
    
def normalize_data(Xlist, operation=None, operations=None):
    """Normalize data using the specified methods: 'bin'arize, 'L1', 'L2', 'whiten'ing, 
       'bias' (adds 1 to every entry), 'none'
       L1 and L2 are per-sample operations, binarization and whitening are per feature operations"""

    if operation:
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
