import serial

class SerialManager: 
    def __init__(self):
        self.serial = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.01)

    def sendMessage(self, message):
        self.serial.write(message.encode('utf-8'))
      
    def receiveMessage(self):
        message = self.serial.readline()
        if(message):
            return message.decode('utf-8').strip()
        else:
            return None