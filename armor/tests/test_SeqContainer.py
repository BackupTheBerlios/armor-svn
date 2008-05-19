import random
import unittest
from armor.SeqContainer import SeqContainer
import armor.prototype

class TestSeqContainer(unittest.TestCase):
    def testInvalidInput(self):
	self.assertRaises(TypeError, SeqContainer, (1,2,3))
	self.assertRaises(TypeError, SeqContainer, {'test':1})
	self.assertRaises(TypeError, SeqContainer, 'teststring')
	self.assertRaises(TypeError, SeqContainer, 1)
	self.assertRaises(TypeError, SeqContainer, None)
	self.assertRaises(TypeError, SeqContainer, [1,2,3], useGenerator=True)
	
    def testCorrectInput(self):
	SeqContainer(range(10))
	SeqContainer(self.iterator)
	SeqContainer(self.iterator, useGenerator=True)

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
	producer = armor.prototype.Producer(self.iterator, useGenerator=True)
	consumer1 = armor.prototype.SeqProcessor(producer.outContainer)
	consumer2 = armor.prototype.SeqProcessor(producer.outContainer)
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
	self.seqContainer = SeqContainer(range(10))	

class TestGenerator(TestSeqContainer):
    def setUp(self):
	self.seqContainer = SeqContainer(self.iterator, useGenerator=True)

class TestGeneratorToList(TestSeqContainer):
    def setUp(self):
	self.seqContainer = SeqContainer(self.iterator, useGenerator=False)


testAll = ['testIterating', 'testToList', 'testGroup']

def suiteInput():
    tests = ['testInvalidInput', 'testCorrectInput']
    return unittest.TestSuite(map(TestSeqContainer, tests))

def suiteList():
    return unittest.TestSuite(map(TestList, testAll))

def suiteGenerator():
    return unittest.TestSuite(map(TestGenerator, testAll))

def suiteGeneratorToList():
    return unittest.TestSuite(map(TestGeneratorToList, testAll))

unittest.TextTestRunner(verbosity=2).run(suiteInput())
unittest.TextTestRunner(verbosity=2).run(suiteList())
unittest.TextTestRunner(verbosity=2).run(suiteGenerator())
unittest.TextTestRunner(verbosity=2).run(suiteGeneratorToList())
