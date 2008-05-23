from types import ListType, MethodType
import itertools
import armor

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
    def __init__(self, seq, slot=None, processFunc=None, labels=None, owner=None, classes=None, useGenerator=armor.useGenerator, **kwargs):
        self.slot = slot
        self.processFunc = processFunc
        
        self.owner = owner
        self.useGenerator = useGenerator
        self.seq = seq
        self.labels = labels
        
        self.getDataAsIter() # Check if seq parameter is sane
        
        self.classes = classes 
        self.__dict__.update(**kwargs)
        self.references = {}   # Registered objects with appropriate group ID
        self.iterpool = {}     # For storing the iterators of each
                               # group until every group member
                               # received it
        self.iterator = None
        
    def getDataAsIter(self):
        """Return the stored data in a way it can be passed to iter()."""
        if isinstance(self.seq, ListType):
            if self.useGenerator:
                # Makes no sense to use generator here
                self.useGenerator = False
                #raise TypeError, 'Setting a list to be used as a generator makes no sense!'
            data = self.seq
            
        elif isinstance(self.seq, MethodType):
            # Input type is a generator, a slot and a functToCall should be set
            if not self.slot or not self.processFunc:
                raise ValueError, "slot and processFunc need to be set"
            if self.useGenerator:
                data = self.seq(self.slot, self.processFunc) # Call the generator
            else:
                self.seq = list(self.seq(self.slot, self.processFunc))
                data = self.seq

        else:
            raise TypeError, "List or Generator expected"

        return data

    def __iter__(self):
        self.iterator = iter(self.getDataAsIter())  # Create a single
                                        # iterator for every object.
        return self.iterator

    def reset(self, group=None):
        """Resets the internal iterator."""
        if not group:
            self.iterator = None
        
    def register(self, reference, group=None):
        """Register an object and add it to group. Registered objects
        in the same group receive cached iterators (for more details
        see the description of the SeqContainer class)"""
        if not self.owner:
            raise ValueError, 'owner must be set to use this feature'
        self.references[reference] = group
        self.owner.register(self, group=group) # The object containing
                                        # SeqContainer must support
                                        # this as well as we need to
                                        # propagate the group
                                        # memberships to the
                                        # SeqContainers we (maybe)
                                        # pool from
        self.iterpool[group] = []
        
    def getIter(self, group=None):
        if not group:
            return self.__iter__()

        if not group in self.iterpool:
            raise KeyError, "You have to register() the group before accessing an iterator from it"
        if len(self.iterpool[group]) == 0:
            # How many streams belong to 'group'?
            count = sum((x for x in self.references.values() if x==group))
            # Create a pool of cached iterators for that group
            self.iterpool[group] = list(itertools.tee(self.getDataAsIter(), count))

        # Hand one cached iterator to the group member.
        return self.iterpool[group].pop()


class slots(object):
    def __init__(self):
	pass
    
    def __getitem__(self, item):
	pass
    
class inputSlot(object):
    def __init__(self, datatype, container, processFunc=None, group=None):
        self.datatype = datatype
        self.container = container
        self.converters = False
        self.group = group
        
    def registerInput(self, senderSlot):
        self.converters = self.datatype.compatible(senderSlot.datatype)
        if self.converters == False:
            raise TypeError, "Slots are not compatible"


    def convert(self, item):
        if self.converters == False or len(self.converters) == 0:
            return item

        for convert in self.converters:
            item = convert(item)

        return item

    def register(self, reference, group=None):
        """Register to group."""
        self.group = group
        # Propagate further
        self.container.register(group)
    
        
class outputSlot(object):
    def __init__(self, datatype, container):
        self.datatype = datatype
        self.container = container
