import mpi_kmeans
import types
import numpy as npy
from scipy import cluster
import armor.prototypes

class kmeansObj(armor.prototypes.BulkProcessor):
    """Class to perform kmeans clustering on input data (e.g. descriptors).
    Returns a codebook.
    For performance reasons we use the kmeans implementation of Peter Gehler
    (pgehler@tuebingen.mpg.de, URL: http://mloss.org/software/view/48/)

    Default is lazy, so the clustering will only be performed when it gets
    accessed."""
    def __init__(self, inContainer, numClusters, maxiter=0, numruns=1, useGenerator=armor.useGenerator):
	super(kmeansObj, self).__init__(inContainer, useGenerator)
        self.numClusters = numClusters
        self.maxiter = maxiter
        self.numruns = numruns

    def process(self, data, labels):
	# Flatten the list (if we get descriptors, we get a list of 2-D arrays)
	if isinstance(data, types.ListType):
	    if isinstance(data[0], npy.ndarray):
		data = npy.concatenate(data)

	# Perform KMeans clustering
	self.codebook, self.dist, self.labels = mpi_kmeans.kmeans(data.T, self.numClusters, self.maxiter, self.numruns)

	return self.codebook
	    
#    def quantize(self):
#	self.dataClusters = []
#	
#	for vecs in self.data:
#	    dataCluster = cluster.vq.vq(vecs[0], self.clusters)
#	    self.dataClusters.append((dataCluster[0], vecs[1]))

    #==============
#    def histogram(self):
#    #==============
#       self.dataHistogram = []

#	for (dataCluster, classID) in self.dataClusters:
#	    histo = npy.histogram(dataCluster, bins = self.numClusters)
#	    self.dataHistogram.append((histo[0], classID))
