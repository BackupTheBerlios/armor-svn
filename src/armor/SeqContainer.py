import itertools
import armor
import weakref

class SeqContainer(object):
    """Central class to store sequential data. It has basic
    list properties with some additional features:
    - Instead of a list, a generator function (NOT the called
    generator function) can be used, it will only get called and
    evaluated when the data is really needed (i.e. lazy evaluation).
    - Once data has been pooled from SeqContainer it will be reset
    so it is possible to iterate multiple times over the same
    SeqContainer.
    - You can have multiple references iterating over SeqContainer as
    every reference will receive its own iterator.
    """
    def __init__(self, sequence=None, generator=None, classes=None, useLazyEvaluation=armor.useLazyEvaluation, useCaching=armor.useCaching):
        self.sequence = sequence
	self.generator = generator
        self.useLazyEvaluation = useLazyEvaluation
	self.useCaching = useCaching
        self.classes = classes

        self.references = weakref.WeakValueDictionary()    # Registered objects with appropriate group ID
        self.iterpool = []     # For storing the iterators of each
                               # group until every group member
                               # received it
        
    def getDataAsIter(self):
        """Return the stored data in a way it can be passed to iter()."""
	if self.generator is not None and self.sequence is None:
	    # Input type is a generator function (hopefully)
	    if self.useLazyEvaluation:
		data = self.generator() # Call the generator
	    else:
		# Convert generator to sequence
		generator = self.generator()
		self.sequence = list(generator)
		self.generator = None
		data = self.sequence
	elif self.sequence is not None and self.generator is None:
	    if self.useLazyEvaluation:
		# Makes no sense to use generator here
		self.useLazyEvaluation = False
	    data = self.sequence
	else:
	    raise NotImplementedError, "generator AND sequence given"

        return data

    def __iter__(self):
	if len(self.references) <= 1:
            return iter(self.getDataAsIter())

        if len(self.iterpool) == 0:
            # Create a pool of cached iterators
            self.iterpool = list(itertools.tee(self.getDataAsIter(), len(self.references)))

        # Hand one cached iterator to the group member.
        return self.iterpool.pop()
    
    def registerReference(self, obj):
        """Register an object. Registered objects receive cached
        iterators (for more details see the description of the
        SeqContainer class)"""
	if self.useCaching:
	    self.references[id(obj)] = obj