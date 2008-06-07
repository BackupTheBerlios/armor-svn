from numpy import array,median,std,mean,log,concatenate,sum,reshape,sqrt,dot,exp,histogram,float,empty,unique
from ctypes import c_double
import armor
import armor.datatypes
import armor.slots
from mpi_kmeans import kmeans as mpi_kmeans

class Score(object):
    def __init__(self, scoretype='clustering', useLazyEvaluation=armor.useLazyEvaluation):
        self.scoretype = scoretype
        if self.scoretype not in ['clustering']:
            raise NotImplementedError, "No such score type"


        self.inputTypeData = armor.datatypes.VectorType(shape=['flatarray'], bulk=True)
        self.inputTypeLabels = armor.datatypes.VectorType(name=['labels'], shape=['flatlist'])
        
        self.outputType = armor.datatypes.VectorType(shape='flatarray')

        self.inputSlotData = armor.slots.InputSlot(name='untransformed',
                                                  acceptsType=self.inputTypeData)

        self.inputSlotLabels = armor.slots.InputSlot(name='labels',
                                                    acceptsType=self.inputTypeLabels)

        self.outputSlot = armor.slots.OutputSlot(name='transformed',
                                                outputType=self.outputType,
                                                useLazyEvaluation=useLazyEvaluation,
                                                iterator=armor.weakmethod(self, 'iterator'))

    def iterator(self):
        # Pool data
        data = array(list(self.inputSlotData), dtype=c_double)
        labels = array(list(self.inputSlotLabels))


        # Transform labels to integers
        labelsint = empty(labels.shape, dtype=int)
        classes = self.inputSlotLabels.senderSlot().container.classes
        for i,classname in enumerate(classes):
            labelsint[labels==classname] = i
            
        if armor.verbosity>0:
            print "Scoring: %s..." % self.scoretype

        score = score_one_clustering(data, labelsint, len(classes), 20)

        yield score


# The following code was kindly provided by Christoph Lampert
# (christoph.lampert@tuebingen.mpg.de) and comes under the
# Apache-License



def chl_entropy(y, base=2):
    """Calculate entropy of a discrete distribution/histogram"""
    p,bins = histogram(y, bins=unique(y))  # don't use 'Normed' feature, since that includes the bin-width!
    p = p[p!=0]/float(len(y))
    S = -1.0*sum(p*log(p))/log(base)
    return S


def condentropy(truelabels, labels):
    """Calculate conditional entropy of one label distribution given 
    another label distribution"""
    labels=array(labels)
    truelabels=array(truelabels)
    
    condent=0.
    for l in xrange(min(labels),max(labels)+1):
        sublabels = truelabels[ labels==l ]
        condent += len(sublabels)*chl_entropy( sublabels )
    return condent/float(len(labels))

def score_one_clustering(X, truelabels, num_components, num_iterations):
    """Cluster a dataset and evaluate it using Conditional Entropy"""
    #scipy's builtin K-means is very slow, use mpi-version instead.
    #from scipy.cluster.vq import kmeans,vq
    #clst,dist =  kmeans(X, num_components, NUM_ITERATIONS)
    #labels,dist =  vq(X, clst)
    clst,dist,labels = mpi_kmeans(X, num_components, 200, num_iterations)
    print truelabels
    print labels-1
    return condentropy(truelabels,labels-1)


# def score_one_mixture(X):
#     """Estimate a Gaussian mixture model from a dataset and evaluate it using 
#        Conditional Entropy
#        This version uses scipy.pyem, but seems fail from time to time."""

#     from scipy.sandbox.pyem import GM, GMM, EM
#     X = X/numpy.mean(X) # isotropic normalization to avoid unstable Gaussians
#     lgm = GM(X.shape[1], num_components, 'diag')
#     gmm = GMM(lgm, 'kmean') # initialize by kmeans
#     gmm.init_kmean(X)
#     em = EM()
#     like =em.train(X, gmm, maxiter=10, thresh=1e-6)
#     try:
#        posterior,dummy = gmm.sufficient_statistics(X)
#     except AttributeError: # upcoming API change
#        posterior,dummy = gmm.compute_responsabilities(X)
#     labels = pylab.argmax(posterior,axis=1)
#     return condentropy(truelabels,labels+1)
