from glob import glob
import os
import os.path
import xml.dom.minidom
import numpy as npy
from PIL import Image
import armor.prototypes

#****************************************************************
class ImageBase(object):
# Base class with all the functional
#****************************************************************
    def __init__(self):
 	self.datasetPath = os.path.join(armor.__path__[0], 'datasets')

	
    #=================
    def loadOneImage(self, file, flatten=True, resize=False, verbose=True):
	"""Loads the image with filename 'file' and returns the PIL.Image object"""
    #=================
        try:
	    if verbose: print(self.absFName(file))
            im=Image.open(self.absFName(file))
            if resize:
                im = im.resize((160, 160), Image.ANTIALIAS)
            if flatten:
                im = im.convert('L')
        except IOError:
#            print("Could not read " + file + "! - Omitting!")
	    raise IOError, 'Could not read %s!' % file
        return (im)


    #==============
    def normalize(self, imgs, minimax = [None, None]):
        """Scales the input matrix to lie between 0 and 1 or minimax if supplied"""
    #==============
        if minimax[0]==None:
            minimax[0] = min(imgs)
        if minimax[1]==None:
            minimax[1] = max(imgs)

        normalized = (imgs-minimax[0])/(float(minimax[1]-minimax[0]))
        return (normalized, minimax)

    #==============
    def randperm(self,(seq)):
        """Randomly permutes the sequences in the seq tuple, however, 
        every sequence gets permuted in the same order"""
    #==============
        from numpy.random import permutation
        l = list()
        perm = permutation(len(seq[0]))
        for i in seq:
            l.append(npy.array(i)[perm])
        return l

    #==============
    def split(self, (lst), ratio=.5): #=round(imgs/2)):
	"""Split the input list and return two lists with the given ratio""" 
    #==============
        length=int(round(len(lst)*ratio))
        return (lst[0:length], lst[length:len(lst)])

    def absFName(self, fname):
	if fname[0] == '.': #relative path given
	    return os.path.join(self.datasetPath, fname)
	else:
	    return fname


#****************************************
class ImageDataset(ImageBase, armor.prototypes.Producer):
#****************************************
#==================================
    def __init__(self, categories=None, splitRatio=.5, doPermutate=False):
#==================================
        super(ImageDataset, self).__init__()
        if not categories:
            categories = []
        self.categories = categories
        self.splitRatio = splitRatio
        self.doPermutate = doPermutate
	self.allFNames = None
	self.allIDs = None
	self.classes = None


    def __iter__(self):
	return iter(self.categories)
    
#==================================
    def prepare(self, useGenerator=True):
        """Once all files are added to the dataset this function is called
        to create a list of all images of all categories, this list is then
        permutated and split into a training and validation set"""
#==================================
        # Create list with all filenames and their class IDs

	self.allFNames = []
	self.allIDs = []
	self.classes = set()
	
        for category in self:
	    self.classes.add(str(category.name))
	    for fname in category:
		self.allFNames.append(self.absFName(fname))
		self.allIDs.append(str(category.name))

        self.outContainer = armor.SeqContainer.SeqContainer(self.iterator, \
							    owner=self, \
                                                            classes=self.classes, \
                                                            useGenerator=useGenerator)
        # Permutate them
#        if self.doPermutate:
#            permutated = self.randperm((self.allFNames, self.allIDs))
#            allFNamesIDs = permutated

        # Split them into training and validation set
#        (self.allNamesTrain, self.allNamesValid) = self.split(self.allFNames, self.splitRatio)
#        (self.allIDsTrain, self.allIDsValid) = self.split(self.allIDs, self.splitRatio)

#===================================
    def iterator(self): #, imgSequence = None, idSequence = None):
        """Generator function that yields one PIL image and its category 
        (can be either self.all(Names,IDs)Train oder self.all(Names,IDs)Valid)"""
#===================================
        # Yield the images element wise
        for img,id in zip(self.allFNames, self.allIDs):
            yield (self.loadOneImage(img), id)
	
#==================================
    def loadFromXML(self, filename, verbose=False):
#==================================
        """Load a dataset in xml format from filename and return it"""
        dom = xml.dom.minidom.parse(filename)
        def getText(nodelist):
            rc = ""
            for node in nodelist:
                if node.nodeType == node.TEXT_NODE:
                    rc = rc + node.data
            return rc

        def handleImgDatasets(xmlImgDatasets):
	    if verbose:	print "<imgdataset>"
            imgDatasets = xmlImgDatasets.getElementsByTagName("category")
            for imgDataset in imgDatasets:
                categoryname = handleTitle(imgDataset.getElementsByTagName("title")[0])
                fnames = handleFilenames(imgDataset.getElementsByTagName("filename"))
                # Create the category and append it to the dataset
                self.addCategory(name=categoryname,fnames=fnames)
	    if verbose: print "</imgdataset>"


        def handleTitle(title):
	    if verbose: print "<title>%s</title>" % getText(title.childNodes)
            return getText(title.childNodes)

        def handleFilenames(xmlFilenames):
            filenames = []
            for filename in xmlFilenames:
                filenames.append(getText(filename.childNodes))
		if verbose: print "<filename>%s</filename>" % getText(filename.childNodes)
            
            return filenames

        handleImgDatasets(dom)

#==================================
    def saveToXML(self, fnameToSave, URL=None, info=None):
#==================================
        """Save datasets to fnameToSave in xml format"""
        xmldoc = xml.dom.minidom.getDOMImplementation()
        newdoc = xmldoc.createDocument(None, "imgdataset", None)
	# Add URL
	if not URL:
	    URL = ""
	urldoc = newdoc.createElement("URL")
	urltext = newdoc.createTextNode(URL)
	urldoc.appendChild(urltext)
	newdoc.childNodes[0].appendChild(urldoc)

	# Add info
	if not info:
	    info = ""
	infodoc = newdoc.createElement("info")
	infotext = newdoc.createTextNode(info)
	infodoc.appendChild(infotext)
	newdoc.childNodes[0].appendChild(infodoc)
	

        for category in self.categories:
            imgdataset = newdoc.createElement("category")
        
            title = newdoc.createElement("title")
            titletext = newdoc.createTextNode(category.name)
            title.appendChild(titletext)
            imgdataset.appendChild(title)
            
            for fname in category.fnames:
                filename = newdoc.createElement("filename")
                filenametext = newdoc.createTextNode(fname)
                filename.appendChild(filenametext)
                imgdataset.appendChild(filename)

            newdoc.childNodes[0].appendChild(imgdataset)

        try:
            fdToSave = open(fnameToSave, 'w')
            newdoc.writexml(fdToSave)
        finally:
            del fdToSave

#==================================
    def addCategory(self, name=None, fnames=None):
#==================================
        if not name:
	    name = ""
        if not fnames:
            fnames = []
        self.categories.append(ImageCategory(name=name, fnames=fnames))
	# Return added element
	return self.categories[-1]

#==================================
    def delCategory(self, id):
#==================================
        del self.categories[id]

#=================================
    def addAutomatic(self, path):
	"""Try to automatically generate a new dataset by treating the
	directory names as categories and the filnames in it as the images
	belonging to that category"""
	path = os.path.abspath(path)
	# Paths in armor/datasets can use '.'
	if os.path.split(path)[0] == self.datasetPath:
	    path = os.path.join('.', os.path.split(path)[1])
	    for counter, (catPath, catN, catFiles) in enumerate(os.walk(os.path.join(self.datasetPath, path))):
		if counter == 0: # first iteration is the base dir, we want subdirs
		    continue
		dirName = os.path.split(catPath)[1]
		self.addCategory(name=dirName, fnames = [os.path.join(path, dirName, fname) for fname in catFiles])
	# Others use the absolute path
	else:
	    for counter, (catPath, catN, catFiles) in enumerate(os.walk(path)):
		if counter == 0: # first iteration is the base dir, we want subdirs
		    continue
		self.addCategory(name=os.path.split(catPath)[1], fnames = [os.path.join(catPath, fname) for fname in catFiles])
	


#************************************************************
class ImageCategory(ImageBase):
#************************************************************
#==================================
    def __init__(self, name="", fnames=None):
#==================================
        ImageBase.__init__(self)
        if not fnames:
            fnames = []
        self.baseDir = os.getcwd()
        self.fnames = fnames
        self.name = name

    def __call__(self):
	return self.name

    def __iter__(self):
	return iter(self.fnames)

#==================================
    def addFile(self, absFileName):
#==================================
        # Replace the dir with "." or ".." if the files reside in the orange directory
        # (makes creating datasets for other people usage easier
        (completePath, fname) = os.path.split(str(absFileName))
        (subPath, dirname) = os.path.split(completePath)
        if self.baseDir == subPath:
            absFileName = os.path.join(".", dirname, fname)
        self.fnames.append(absFileName)

#==================================
    def addFiles(self, absFileNames):
#==================================
        for absFileName in absFileNames:
            self.addFile(absFileName)

#==================================
    def addDir(self, dirName):
#==================================
        absFileNames = glob(os.path.join(str(dirName), "*.*"))
        self.addFiles(absFileNames)

#==================================
    def delFile(self, fnameToDel):
#==================================
        for (id,fname) in enumerate(self.fnames):
            if fname == fnameToDel:
                del self.fnames[id]
                break

#==================================
    def delID(self, idToDel):
#==================================
        del self.fnames[idToDel]
