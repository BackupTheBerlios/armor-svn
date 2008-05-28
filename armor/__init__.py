# set default to use lazy evaluation where possible
useGenerator=True
useTypeChecking=True
verbosity=1


def saveSlots(outputSlots, fname):
    import pickle

    # First, let every output slot process and save all the data
    # Also, remove all instancemethods
    for slot in outputSlots:
	slot.container.useGenerator=False
	slot.container.getDataAsIter()
	slot.seqIterator = None
	slot.bulkIterator = None
	slot.processFunc = None
	slot.processFuncs = None
	slot.inputSlot = None
	
    try:
	fdescr = open(fname, mode='w')
	pickle.dump(outputSlots, fdescr)
    finally:
	del fdescr

    
def loadSlots(fname):
    import pickle
    import armor.slot

    try:
	fdescr = open(fname, mode='r')
	outputSlots = pickle.load(fdescr)
    finally:
	del fdescr

    return armor.slot.slots(outputSlots)
    
	
    
