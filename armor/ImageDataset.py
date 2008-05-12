from glob import glob
import os
import os.path
import xml.dom.minidom
import numpy as npy
from PIL import Image
import armor

#****************************************************************
class ImageBase(object):
# Base class with all the functional
#****************************************************************
    #=================
    def loadOneImage(self, file, flatten=True, resize=False):
    # Loads the image with filename 'file' and returns the PIL.Image object
    #=================
        try:
            print(file)
            im=Image.open(file)
            if resize:
                im = im.resize((160, 160), Image.ANTIALIAS)
            if flatten:
                im = im.convert('L')
        except IOError:
#            print("Could not read " + file + "! - Omitting!")
	    raise(IOError, 'Could not read ' + file + '!')
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
    #==============
        length=int(round(len(lst)*ratio))
        return (lst[0:length], lst[length:len(lst)])


#****************************************
class ImageDataset(ImageBase):
#****************************************
#==================================
    def __init__(self, groups=None, splitRatio=.5, doPermutate=False):
#==================================
        if not groups:
            groups = []
        self.groups = groups
        self.splitRatio = splitRatio
        self.doPermutate = doPermutate
	self.allFNames = None
	self.allIDs = None
	self.classes = None
	
    def getData(self, useGenerator=False):
        if not self.allFNames:
            self.prepareSet()
	return armor.SeqContainer(self.iterator, classes=self.classes, useGenerator=useGenerator)
	

    def __iter__(self):
	return iter(self.groups)
    
#==================================
    def prepareSet(self):
        """Once all files are added to the dataset this function is called
        to create a list of all images of all groups, this list is then
        permutated and split into a training and validation set"""
#==================================
        # Create list with all filenames and their class IDs

	self.allFNames = []
	self.allIDs = []
	self.classes = set()
	
        for group in self:
	    self.classes.add(group.name)
            for fname in group:
                self.allFNames.append(fname)
                self.allIDs.append(group.name)
        
        # Permutate them
#        if self.doPermutate:
#            permutated = self.randperm((self.allFNames, self.allIDs))
#            allFNamesIDs = permutated

        # Split them into training and validation set
#        (self.allNamesTrain, self.allNamesValid) = self.split(self.allFNames, self.splitRatio)
#        (self.allIDsTrain, self.allIDsValid) = self.split(self.allIDs, self.splitRatio)

#===================================
    def iterator(self): #, imgSequence = None, idSequence = None):
        """Generator function that yields one PIL image and its group 
        (can be either self.all(Names,IDs)Train oder self.all(Names,IDs)Valid)"""
#===================================
        # Yield the images element wise
        for img,id in zip(self.allFNames, self.allIDs):
            yield (self.loadOneImage(img), id)
	
#==================================
    def loadFromXML(self, filename):
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
            print "<imgdataset>"
            imgDatasets = xmlImgDatasets.getElementsByTagName("imgdataset")
            for imgDataset in imgDatasets:
                groupname = handleTitle(imgDataset.getElementsByTagName("title")[0])
                fnames = handleFilenames(imgDataset.getElementsByTagName("filename"))
                # Create the group and append it to the dataset
                self.addGroup(name=groupname,fnames=fnames)
            print "</imgdataset>"


        def handleTitle(title):
            print "<title>%s</title>" % getText(title.childNodes)
            return getText(title.childNodes)

        def handleFilenames(xmlFilenames):
            filenames = []
            for filename in xmlFilenames:
                filenames.append(getText(filename.childNodes))
                print "<p>%s</p>" % getText(filename.childNodes)
            
            return filenames

        handleImgDatasets(dom)

#==================================
    def saveToXML(self, fnameToSave):
#==================================
        """Save datasets to fnameToSave in xml format"""
        xmldoc = xml.dom.minidom.getDOMImplementation()
        newdoc = xmldoc.createDocument(None, "imgdatasets", None)

        for group in self.groups:
            imgdataset = newdoc.createElement("imgdataset")
        
            title = newdoc.createElement("title")
            titletext = newdoc.createTextNode(group.name)
            title.appendChild(titletext)
            imgdataset.appendChild(title)
            
            for fname in group.fnames:
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
    def addGroup(self, name="", fnames=None):
#==================================
        if not fnames:
            fnames = []
        self.groups.append(ImageGroup(name=name, fnames=fnames))

#==================================
    def delGroup(self, id):
#==================================
        del self.groups[id]        
    
#************************************************************
class ImageGroup(ImageBase):
#************************************************************
#==================================
    def __init__(self, name="", fnames=None):
#==================================
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
