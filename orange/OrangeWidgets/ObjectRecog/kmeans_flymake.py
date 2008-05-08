import mpi_kmeans
import types
import numpy as npy

class kmeans:
    def __init__(self, X, numClusters, maxiter=0, numruns=1):
        self.X = X

        self.numClusters = numClusters
        self.maxiter = maxiter
        self.numruns = numruns

    def runKmeans(self):
        # If we got passed a generator we have to
        # convert it to a list here.
        if type(self.X) is types.GeneratorType:
            self.X = list(self.X)

            clst, dist, labels = mpi_kmeans.kmeans(self.X, self.numClusters, self.maxiter, self.numruns)
        
        
        
    #==============
    def histogram(self, vecs, codebook):
    #==============
        hist = npy.zeros((len(codebook)))
        for vec in vecs:
            for index, cluster in enumerate(codebook):
                if (vec == cluster).all():
                    hist[index] += 1

        return hist
