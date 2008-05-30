# set default to use lazy evaluation where possible
useGenerator=True
useTypeChecking=True
useGrouping=True
groupCounter=0
verbosity=1
useOrange=True

def stripSlot(slot):
    import pickle
    slot.container.useGenerator=False
    slot.container.getDataAsIter()
    slot.seqIterator = None
    slot.bulkIterator = None
    slot.processFunc = None
    slot.processFuncs = None
    slot.inputSlot = None

def saveSlots(fname, outputSlot=None, outputSlots=None):
    import pickle

    # First, let every output slot process and save all the data
    # Also, remove all instancemethods
    try:
	fdescr = open(fname, mode='w')

	if outputSlot is not None:
	    stripSlot(outputSlot)
	    pickle.dump(outputSlot, fdescr)
	    
	elif outputSlots is not None:
	    for slot in outputSlots:
		stripSlot(slot)
	    pickle.dump(outputSlots, fdescr)
	    
    finally:
	del fdescr

    
def loadSlots(fname):
    import pickle

    try:
	fdescr = open(fname, mode='r')
	outputSlots = pickle.load(fdescr)
    finally:
	del fdescr

    return outputSlots
    
	
    
