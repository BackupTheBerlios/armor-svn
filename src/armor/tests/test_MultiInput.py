import unittest
import armor
import armor.slots

numSlots = 100

class TestMultiInput(unittest.TestCase):
    def setUp(self):
        # Create some output slots
        self.outputSlots = []

        for i in xrange(numSlots):
            self.outputSlots.append(armor.slots.OutputSlot(name=str(i), sequence=range(numSlots)*i, outputType=armor.slots.ImageType()))

        # Create the MultiSlot
        self.inputSlot = armor.slots.MultiInputSlot(name='testCase')

        # Connect outputslots to the multislot
        for outputSlot in self.outputSlots:
            self.inputSlot.registerInput(outputSlot)

    def connected(self, numConnected=numSlots):
        self.assertEqual(len(self.inputSlot.senderSlots), numConnected)

    def iterating(self):
        for idx,output in enumerate(self.inputSlot):
            self.assertEqual(output, [i*idx for i in xrange(numSlots)])

    def testConnected(self):
        self.connected()

    def testIterating(self):
        self.iterating()

    def testDelete(self):
        del self.outputSlots[0]
        self.connected(numConnected=numSlots-1)
        del self.outputSlots[2]
        self.connected(numConnected=numSlots-2)

    def testReconnect(self):
        self.inputSlot.registerInput(self.outputSlots[2])
        self.connected()
        self.iterating()

suite = unittest.TestLoader().loadTestsFromTestCase(TestMultiInput)
unittest.TextTestRunner(verbosity=3).run(suite)
