import unittest
import armor
import armor.slot
import armor.datatypes
import gc

class TestTypes(unittest.TestCase):
    def setUp(self):
        pass
    
    def setTypesNoConversion(self):
        self.outType1 = armor.datatypes.ImageType(format='PIL', color_space='RGB')
        self.inType2 = armor.datatypes.ImageType(format=['PIL'], color_space=['RGB'])
        self.outType2 = armor.datatypes.VectorType(shape='nestedlist')

    def setTypesConversion(self):
        self.outType1 = armor.datatypes.ImageType(format='PIL', color_space='RGB')
        self.inType2 = armor.datatypes.ImageType(format=['PIL'], color_space=['gray'])
        self.outType2 = armor.datatypes.VectorType(shape='nestedlist')

    def setTypesIncompatible(self):
        self.outType1 = armor.datatypes.ImageType(format='PIL', color_space='gray')
        self.inType2 = armor.datatypes.ImageType(format=['PIL'], color_space=['RGB'])
        self.outType2 = armor.datatypes.VectorType(shape='nestedlist')

    def setSlots(self):
        self.slotSend = armor.slot.outputSlot('sender',
                                              iterator=self.iterator,
                                              outputType=self.outType1)

        self.slotInput = armor.slot.inputSlot('input',
                                              acceptsType=self.inType2)
        
        self.slotRecv = armor.slot.outputSlot('receiver',
					      input = self.slotInput,
					      processFunc=self.process,
					      outputType=self.outType2,
					      slotType='sequential')


    def setMultiInput(self):
        self.slotSend = armor.slot.outputSlot('sender', iterator=self.iterator)
        
        self.slotInput1 = armor.slot.inputSlot('input1')
        self.slotInput2 = armor.slot.inputSlot('input2')
        
        self.inputSlots = armor.slot.slots([self.slotInput1, self.slotInput2])
        self.inputSlots['input1'].registerInput(self.slotSend)
        self.inputSlots['input2'].registerInput(self.slotSend)
        
        
    def testSlotConnectNoConversion(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual([i.__name__ for i in self.slotRecv.processFuncs], ['process'])
        
    def testSlotConnectConversion(self):
        self.setTypesConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual([i.__name__ for i in self.slotInput.converters], ['convert_PIL_RGB_to_PIL_gray'])
        self.assertEqual([i.__name__ for i in self.slotRecv.processFuncs], ['process'])

    def testSlotIncompatible(self):
        self.setTypesIncompatible()
        self.setSlots()
        self.assertRaises(TypeError, self.slotInput.registerInput, self.slotSend)
        
    def testIterating(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual([i for i in self.slotRecv], range(10))
        self.assertEqual([i for i in self.slotRecv], range(10))

    def testReconnect(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        self.slotSend = armor.slot.outputSlot('sender',
                                              sequence=range(11),
                                              outputType=self.outType1)
        self.slotInput.registerInput(self.slotSend)
        self.assertEqual([i for i in self.slotRecv], range(11))

    def testMultiInput(self):
        self.setMultiInput()
        self.slotRecv = armor.slot.outputSlot('receiver', iterator=self.iterMulti)
        self.assertEqual([i for i in self.slotRecv], [x+y for x,y in zip(range(10),range(10))])

    def testGroup(self):
        self.setTypesNoConversion()
        self.setSlots()
        self.slotInput.registerInput(self.slotSend)
        
        self.slotInput2 = armor.slot.inputSlot('input2',
                                              acceptsType=self.inType2)
        
        self.slotRecv2 = armor.slot.outputSlot('receiver2',
					       input = self.slotInput2,
					       processFunc=self.process,
					       outputType=self.outType2,
					       slotType='sequential')

        self.slotInput2.registerInput(self.slotSend)

        self.assertEqual([i for i in self.slotRecv], range(10))
        self.assertEqual([i for i in self.slotRecv2], range(10))
        
    def iterMulti(self):
        input1 = list(self.inputSlots['input1'])
        for count,i in enumerate(self.inputSlots['input2']):
            yield input1[count] + i
        
    def process(self, item):
        return item

    def iterator(self):
        for i in xrange(10):
            yield i

suite = unittest.TestLoader().loadTestsFromTestCase(TestTypes)
unittest.TextTestRunner(verbosity=3).run(suite)
