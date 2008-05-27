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
    def __init__(self, sequence=None, generator=None, slot=None, labels=None, classes=None, useGenerator=armor.useGenerator):
        self.sequence = sequence
        self.generator = generator
        self.useGenerator = useGenerator        
        self.getDataAsIter() # Check if input parameters are sane
        self.slot = slot 

        self.labels = labels
        self.classes = classes

        #        self.__dict__.update(**kwargs)
        self.references = {}   # Registered objects with appropriate group ID
        self.iterpool = {}     # For storing the iterators of each
                               # group until every group member
                               # received it
        
    def getDataAsIter(self):
        """Return the stored data in a way it can be passed to iter()."""
	try:
	    if self.generator and not self.sequence:
		# Input type is a generator function (hopefully)
		if self.useGenerator:
		    data = self.generator() # Call the generator
		else:
		    # Convert generator to sequence
		    self.sequence = list(self.generator())
		    self.generator = None
		    data = self.sequence
	    elif self.sequence and not self.generator:
		if self.useGenerator:
		    # Makes no sense to use generator here
		    self.useGenerator = False
		    #raise TypeError, 'Setting a list to be used as a generator makes no sense!'
		data = self.sequence
	    else:
		raise NotImplementedError, "generator AND sequence given"

        except ValueError: # for numpy funkyness
	    if self.generator:
		raise NotImplementedError, "generator AND sequence given"
	    if self.useGenerator:
		# Makes no sense to use generator here
		self.useGenerator = False
		#raise TypeError, 'Setting a list to be used as a generator makes no sense!'
	    data = self.sequence
	    
        return data

    def __iter__(self):
        iterator = iter(self.getDataAsIter())  # Create a single
                                        # iterator for every object.
        return iterator

    def registerGroup(self, reference=None, group=None):
        """Register an object and add it to group. Registered objects
        in the same group receive cached iterators (for more details
        see the description of the SeqContainer class)"""
        if not self.slot:
            raise ValueError, 'slot must be set to use this feature'

        if not group in self.references:
            self.references[group] = 1
        else:
            self.references[group] += 1
            
        self.iterpool[group] = []
        
    def getIter(self, group=None):
        if not group:
            return self.__iter__()

        if not group in self.iterpool:
            raise KeyError, "You have to register() the group before accessing an iterator from it"
        if len(self.iterpool[group]) == 0:
            # Create a pool of cached iterators for that group
            self.iterpool[group] = list(itertools.tee(self.getDataAsIter(), self.references[group]))

        # Hand one cached iterator to the group member.
        return self.iterpool[group].pop()


