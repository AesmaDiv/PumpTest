# adam = Adam5K('10.10.10.10', 502, 1)
# adam.connect()
# adam.setReadingThread(True)
# adam.setSlot(Adam5K.SlotType.DIGITAL, 0, [True] * 8 * 4)
# adam.setSlot(Adam5K.SlotType.DIGITAL, 3, [True] * 8 * 4)
# while adam.isBusy():
#     sleep(1.5)
#     pass
# adam.setReadingThread(False)
# adam.disconnect(False)