import mpi_kmeans
import types
import numpy as npy
from scipy import cluster

class kmeans:
    def __init__(self, data, numClusters, maxiter=0, numruns=1):
	#if we get passed a generator function, we first have to call it
	if type(data) is types.MethodType:
	    self.data = list(data())
	#if type(data) is types.ListType or type(data) is npy.ndarray: 
	else:
	    self.data = data

        self.numClusters = numClusters
        self.maxiter = maxiter
        self.numruns = numruns

	self.runKmeans()
	self.quantize()
	self.histogram()
	
    def runKmeans(self):
	# For the clustering we need the data without labels and 
        # If we got passed a generator we have to convert it to a list here (by list(self.data)).
#	if type(self.data) is types.GeneratorType:
#	    self.data = list(self.data)

	# Also, remove the labels
	data = [x[0] for x in self.data]
	# Flatten the list (if we get descriptors, we get a list of 2-D arrays)
	if type(data[0]) is npy.ndarray:
	    data = npy.concatenate(data)
	self.dataClusters = []

	# Perform KMeans clustering
	self.clusters, self.dist, self.labels = mpi_kmeans.kmeans(data, self.numClusters, self.maxiter, self.numruns)
	    
    def quantize(self):
	self.dataClusters = []
	
	for vecs in self.data:
	    dataCluster = cluster.vq.vq(vecs[0], self.clusters)
	    self.dataClusters.append((dataCluster[0], vecs[1]))
	    
	
        
    #==============
    def histogram(self):
    #==============
        self.dataHistogram = []

	for (dataCluster, classID) in self.dataClusters:
	    histo = npy.histogram(dataCluster, bins = self.numClusters)
	    self.dataHistogram.append((histo[0], classID))
