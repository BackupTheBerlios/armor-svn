import unittest
from armor.SeqContainer import SeqContainer
import armor.prototypes

class TestSeqContainer(unittest.TestCase):
    def testInvalidInput(self):
        self.assertRaises(TypeError, SeqContainer, (1,2,3))
        self.assertRaises(TypeError, SeqContainer, {'test':1})
        self.assertRaises(TypeError, SeqContainer, 'teststring')
        self.assertRaises(TypeError, SeqContainer, 1)
        self.assertRaises(TypeError, SeqContainer, None)
        
    def testCorrectInput(self):
        SeqContainer(range(10))
        SeqContainer(self.iterator)
        SeqContainer(self.iterator, useLazyEvaluation=True)

    def testIterating(self):
        iterator = self.seqContainer
        for i,j in zip(iterator, range(10)):
            self.assertEqual(i,j, 'Values do not match')

    def iterator(self):
        for i in range(10):
            yield i

    def testToList(self):
        self.assertEqual(list(self.seqContainer), range(10))

    def testGroup(self):
        producer = armor.prototypes.Producer(self.iterator, useLazyEvaluation=True)
	producer.outContainer = SeqContainer(producer.inContainer, \
				  	    owner = producer)
        consumer1 = armor.prototypes.SeqProcessor(producer.outContainer)
        consumer2 = armor.prototypes.SeqProcessor(producer.outContainer)
        self.assertEqual([i for i in producer.outContainer], range(10))
        self.assertEqual([i for i in producer.outContainer], range(10))
        
        consumer1.outContainer.register('test1', group=1)
        consumer2.outContainer.register('test2', group=1)
        self.assertEqual(producer.outContainer.references.values(), [1, 1])
        
        iter1 = consumer1.outContainer.getIter(group=1)
        iter2 = consumer2.outContainer.getIter(group=1)
        self.assertEqual([i for i in iter1], range(10))
        self.assertEqual([i for i in iter2], range(10))

        iter1 = consumer1.outContainer.getIter(group=1)
        iter2 = consumer2.outContainer.getIter(group=1)
        self.assertEqual([i for i in iter1], range(10))
        self.assertEqual([i for i in iter2], range(10))
        
        
        

class TestList(TestSeqContainer):
    def setUp(self):
        self.seqContainer = SeqContainer(range(10), useLazyEvaluation=False)     

class TestGenerator(TestSeqContainer):
    def setUp(self):
        self.seqContainer = SeqContainer(self.iterator, useLazyEvaluation=True)

#class TestGeneratorToList(TestSeqContainer):
#    def setUp(self):
#        self.seqContainer = SeqContainer(self.iterator, useLazyEvaluation=False)


testAll = ['testIterating', 'testToList', 'testGroup']

def suiteInput():
    tests = ['testInvalidInput', 'testCorrectInput']
    return unittest.TestSuite(map(TestSeqContainer, tests))

def suiteList():
    return unittest.TestSuite(map(TestList, testAll))

def suiteGenerator():
    return unittest.TestSuite(map(TestGenerator, testAll))

#def suiteGeneratorToList():
#    return unittest.TestSuite(map(TestGeneratorToList, testAll))

unittest.TextTestRunner(verbosity=2).run(suiteInput())
unittest.TextTestRunner(verbosity=2).run(suiteList())
unittest.TextTestRunner(verbosity=2).run(suiteGenerator())
#unittest.TextTestRunner(verbosity=2).run(suiteGeneratorToList())
