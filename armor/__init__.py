import weakref

# set default to use lazy evaluation where possible
useLazyEvaluation=True
useTypeChecking=True
useCaching=True
groupCounter=0
verbosity=1
useOrange=True

def stripSlot(slot):
    import pickle
    slot.container.useLazyEvaluation=False
    slot.container.getDataAsIter()
    slot.seqIterator = None
    slot.bulkIterator = None
    slot.processFunc = None
    slot.processFuncs = None
    slot.InputSlot = None

def saveSlots(fname, OutputSlot=None, OutputSlots=None):
    import pickle

    # First, let every output slot process and save all the data
    # Also, remove all instancemethods
    try:
	fdescr = open(fname, mode='w')

	if OutputSlot is not None:
	    stripSlot(OutputSlot)
	    pickle.dump(OutputSlot, fdescr)
	    
	elif OutputSlots is not None:
	    for slot in OutputSlots:
		stripSlot(slot)
	    pickle.dump(OutputSlots, fdescr)
	    
    finally:
	del fdescr

    
def loadSlots(fname):
    import pickle

    try:
	fdescr = open(fname, mode='r')
	OutputSlots = pickle.load(fdescr)
    finally:
	del fdescr

    return OutputSlots
    
def applySettings(settingsList, widget, obj=None, kwargs=None):
    changed = False

    if obj is not None:
	for setting in settingsList:
	    try:
		if getattr(obj, setting):
		    if getattr(widget, setting) != getattr(obj, setting):
			setattr(obj, setting, getattr(widget, setting))
			changed = True
	    except AttributeError:
		pass

    if kwargs is not None:
	for setting in settingsList:
	    if setting in kwargs:
		if kwargs[setting] != getattr(widget, setting):
		    kwargs[setting] = getattr(widget, setting)
		    changed = True


    if changed:
	print "Changed"
	return True
	
    return False

def weakmethod(obj, methname):
    r = weakref.ref(obj)
    del obj
    def _weakmethod(*args, **kwargs):
        return getattr(r(), methname)(*args, **kwargs)
    return _weakmethod
