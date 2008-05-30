import itertools
import armor
import weakref

class SeqContainer(object):
    """Central class to store sequential data. It has basic
    list properties with some additional features:
    - Instead of a list, a generator function (NOT the called
    generator function) can be used, it will only get called and
    evaluated when the data is really needed.
    - Once data has been pooled from SeqContainer it will be reset
    so it is possible to iterate multiple times over the same
    SeqContainer.
    - You can have multiple references iterating over SeqContainer as
    every reference will receive its own iterator.
    - Each object with a reference to SeqContainer can register itself
    with a group ID. If multiple objects have the same group ID they
    will all receive a synced iterator that caches each element until
    every object iterated over this element. Thus, if the computation
    of the elements is very expensive and lazy evaluation is used
    (useGenerator=armor.useGenerator) and multiple objects need the same element at
    roughly the same time this can save a lot of useless recomputing
    the same elements for every single object.
    Important: for the last feature to work, the object containing
    SeqContainer must have defined a special register() function (like
    all classes in armor.prototypes do so it is most convenient to
    inherit from the appropriate prototype).
    """
    def __init__(self, sequence=None, generator=None, labels=None, classes=None, useGenerator=armor.useGenerator):
        self.sequence = sequence
	self.generator = generator
	    
        self.useGenerator = useGenerator
        self.labels = labels
        self.classes = classes

        self.references = weakref.WeakValueDictionary()    # Registered objects with appropriate group ID
        self.iterpool = []     # For storing the iterators of each
                               # group until every group member
                               # received it
        
    def getDataAsIter(self):
        """Return the stored data in a way it can be passed to iter()."""
	if self.generator is not None and self.sequence is None:
	    # Input type is a generator function (hopefully)
	    if self.useGenerator:
		data = self.generator() # Call the generator
	    else:
		# Convert generator to sequence
		generator = self.generator()
		self.sequence = list(generator)
		self.generator = None
		data = self.sequence
	elif self.sequence is not None and self.generator is None:
	    if self.useGenerator:
		# Makes no sense to use generator here
		self.useGenerator = False
	    data = self.sequence
	else:
	    raise NotImplementedError, "generator AND sequence given"

        return data

    def __iter__(self):
	if len(self.references) <= 1:
            return iter(self.getDataAsIter())

        if len(self.iterpool) == 0:
            # Create a pool of cached iterators for that group
            self.iterpool = list(itertools.tee(self.getDataAsIter(), len(self.references)))

        # Hand one cached iterator to the group member.
        return self.iterpool.pop()
    
    def registerReference(self, obj, replaces=None):
        """Register an object and add it to group. Registered objects
        in the same group receive cached iterators (for more details
        see the description of the SeqContainer class)"""

	self.references[id(obj)] = obj
	
        



