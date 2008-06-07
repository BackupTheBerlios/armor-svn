import unittest
import armor.ImageDataset
import armor.cluster
import armor.tests
import armor.histogram
import armor.filter
import armor.transforms
import armor.features
import armor.score

import armor
import numpy
import os.path
import gc

class testAll(unittest.TestCase):
    def setUp(self):
        self.path = armor.__path__[0]
        self.pathtest = armor.tests.__path__[0]
        self.imgDataset = armor.ImageDataset.ImageDataset()
        #self.imgDataset.loadFromXML(os.path.join(self.pathtest, 'test_valid.xml'))
        self.imgDataset.loadFromXML(os.path.join(self.path, 'datasets', 'caltech_4_small.xml'))

        self.imgDataset.prepare()

    def createDescr(self):
        ft = armor.filter.Filter(filter='smooth')
        #sft = armor.features.SiftValedi()
        #rce = armor.features.Nowozin('color')
        #rce = armor.features.SiftRobHess()
        rce = armor.features.SiftValedi()
        
        ft.inputSlot.registerInput(self.imgDataset.outputSlotTrain)
        #sft.InputSlot.registerInput(ft.outputSlot)
        rce.inputSlot.registerInput(ft.outputSlot)
        armor.saveSlots('rce.pickle', rce.outputSlot)
        return rce.outputSlot
    
    def testGenerator(self):
        #from IPython.Debugger import Tracer; debug_here = Tracer()
        #debug_here()
        rce = self.createDescr()
        #rce = armor.loadSlots('rce.pickle')
        
        km = armor.cluster.Kmeans(1000)
        qt = armor.cluster.Quantize()
        hg = armor.histogram.Histogram(1000)
        nz = armor.transforms.Normalize('bin')
        tf = armor.transforms.Transform('PCA')
        nz2 = armor.transforms.Normalize('whiten')
        sc = armor.score.Score()
        
        #km.InputSlot.registerInput(sft.OutputSlot)
        #km.InputSlot.registerInput(rce)
        #armor.saveSlots('km.pickle', km.OutputSlot)
        km = armor.loadSlots('km.pickle')
        qt.inputSlotCodebook.registerInput(km)
        #qt.InputSlotVec.registerInput(sft.OutputSlot)
        qt.inputSlotVec.registerInput(rce)
        hg.inputSlot.registerInput(qt.outputSlot)
        nz.inputSlot.registerInput(hg.outputSlot)
        tf.inputSlotData.registerInput(nz.outputSlot)
        tf.inputSlotLabels.registerInput(self.imgDataset.outputSlotLabelsTrain)
        nz2.inputSlot.registerInput(tf.outputSlot)
        sc.inputSlotData.registerInput(tf.outputSlot)
        sc.inputSlotLabels.registerInput(self.imgDataset.outputSlotLabelsTrain)
        
        print list(sc.outputSlot)
        #del sft
        #self.assertRaises(AttributeError, list(hg.OutputSlot))
#       del km
#       self.assertRaises(AttributeError, list(hg.OutputSlot))
        
        #armor.saveSlots('kmeansSlot.pickle', outputSlot = sft.OutputSlot)
        #savedslot = armor.loadSlots('kmeansSlot.pickle')
        #print list(savedslot)
#       assert (list(km.OutputSlot), list(kmSlots['codebook']))
#       print list(km.OutputSlot)[0].shape


        #self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
        #for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
        #    self.assertTrue(all(x[0] == y))
        
#     def testList(self):
#       sft = armor.sift(self.imgDataset.getData())
#       km = armor.cluster(sft.getData(), 3)
#       data = list(km.getData())
#       self.assertEqual([x[1] for x in data], [u'test1', u'test2'])
        #TODO: Call kmeans with fixed start vectors
        #for x,y in zip(data, [numpy.array([475, 693, 531]), numpy.array([566, 782, 509])]):
        #    self.assertTrue(all(x[0] == y))

suite = unittest.TestLoader().loadTestsFromTestCase(testAll)
unittest.TextTestRunner(verbosity=3).run(suite)
