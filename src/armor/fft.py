import armor
import armor.transforms
import armor.ImageDataset

imgDataset = armor.ImageDataset.ImageDataset()
imgDataset.loadFromXML('PNAS.xml')
imgDataset.prepare()

fft = armor.transforms.Fft2()

avg = armor.transforms.Average()

fft.inputSlot.registerInput(imgDataset.outputSlotTrain)
#armor.saveSlots('fft.pickle', fft.outputSlot)
#fft = armor.loadSlots('fft.pickle')


avg.inputSlotLabels.registerInput(imgDataset.outputSlotLabelsTrain)
avg.inputSlotData.registerInput(fft.outputSlot)

list(avg.outputSlot)
