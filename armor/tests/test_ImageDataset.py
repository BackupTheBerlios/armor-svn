import unittest
from armor import ImageDataset
import armor.tests

class TestImageDataset(unittest.TestCase):
    def setUp(self):
	self.ImageDataset = ImageDataset()
	self.path = armor.tests.__path__[0]
	self.setInvalid = [self.path + '/testImgs/nonexisting.jpg', self.path + '/testImgs/test1.jpg']
	self.setValid = [self.path + '/testImgs/test1.jpg', self.path + '/testImgs/test2.jpg']
	
    def addGroups(self, set = None):
	if not set:
	    set = self.setInvalid
	self.ImageDataset.addGroup()
	self.ImageDataset.addGroup('test1')
	self.ImageDataset.addGroup('test2', set)

    def testAddGroups(self):
	self.addGroups()
#	self.ImageDataset.saveToXML('test.xml')
	self.checkConsistency()
	
    def checkConsistency(self):
	self.assertEqual(self.ImageDataset.groups[0].name, '')
	self.assertEqual(self.ImageDataset.groups[1].name, 'test1')
	self.assertEqual(self.ImageDataset.groups[2].name, 'test2')
	self.assertEqual(self.ImageDataset.groups[2].fnames, self.setInvalid)

	
    def testDelGroups(self):
	self.addGroups()
	self.ImageDataset.delGroup(0)
	self.assertEqual(len(self.ImageDataset.groups), 2)
	self.assertEqual(self.ImageDataset.groups[0].name, 'test1')

	self.assertRaises(IndexError, self.ImageDataset.delGroup, 2)
	
	
    def testLoadFromXML(self, fname=None):
	
	if not fname:
	    self.testSaveToXML()
	    fname = self.path + '/test_saved.xml'
	    
	self.ImageDataset.loadFromXML(fname)
	self.checkConsistency()
	
    def testSaveToXML(self):
	self.addGroups()
	self.ImageDataset.saveToXML(self.path + '/test_saved.xml')
	del self.ImageDataset
	self.setUp()
	self.ImageDataset.loadFromXML(self.path + '/test_saved.xml')
	self.checkConsistency()
	
    def testAddAndDelFnames(self):
	self.addGroups()
	self.ImageDataset.groups[1].addDir(self.path + '/testImgs')
	self.assertEqual(self.ImageDataset.groups[1].fnames, self.setValid)
	self.ImageDataset.groups[1].delFile(self.path + '/testImgs/test1.jpg')
	self.assertEqual(self.ImageDataset.groups[1].fnames, [self.path + '/testImgs/test2.jpg'])
	self.ImageDataset.groups[1].delID(0)
	self.assertEqual(len(self.ImageDataset.groups[1].fnames), 0)

    def testIterateGroups(self):
	self.addGroups()
	for x,y in zip(self.ImageDataset, ['', 'test1', 'test2']):
	    self.assertEqual(x.name,y)

    def testIterateFnames(self):
	self.addGroups()
	for x,y in zip(self.ImageDataset.groups[2], [self.path + '/testImgs/nonexisting.jpg', self.path + '/testImgs/test1.jpg']):
	    self.assertEqual(x,y)

    def testSeqContainerValid(self):
	self.addGroups(set = self.setValid)
	seqContainer = self.ImageDataset.getData()
	
    def testSeqContainerValidIter(self):
	self.addGroups(set = self.setValid)
	seqContainer = self.ImageDataset.getData(useGenerator=True)

    def testSeqContainerInvalid(self):
	self.addGroups()
	self.assertRaises(IOError, self.ImageDataset.getData)
	

suite = unittest.TestLoader().loadTestsFromTestCase(TestImageDataset)
unittest.TextTestRunner(verbosity=3).run(suite)
