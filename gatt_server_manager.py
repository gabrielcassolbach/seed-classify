import dbus
import json
import os
import sys

# To notify Pico the connection stablished
from serial_manager import SerialManager

from ble_gatt_server.advertisement import Advertisement
from ble_gatt_server.service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 6000  # Interval for notifications

# Load JSON data
def load_process_data():
    """Load processes from the JSON file."""
    with open("processes_store.json", "r") as file:
        data = json.load(file)
        return data.get("processes", [])

# # Save updated JSON data (clear data)
def clear_process_data():
    """Clear the JSON file after data has been sent."""
    with open("processes_store.json", "w") as file:
        json.dump({"processes":[]}, file)  # Save an empty list

class BleApplication(Application):
    pass

class MachineProcessAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("MachineProcessData")
        self.include_tx_power = True

class ProcessService(Service):
    PROCESS_SVC_UUID = "00000000-8cb1-44ce-9a66-001dca0941a6"
    def __init__(self, index):
        Service.__init__(self, index, self.PROCESS_SVC_UUID, True)
        self.process_data = load_process_data()
        self.add_characteristic(ProcessCharacteristic(self))
        self.JSON_FILE = "processes_store.json"

    def get_process_data(self):
        """Reads and returns the processes from the JSON file."""
        return self.process_data

    def clear_data(self):
        """Clears the processes in the JSON file."""
        clear_process_data()

class ProcessCharacteristic(Characteristic):
    PROCESS_CHARACTERISTIC_UUID = "00000001-8cb1-44ce-9a66-001dca0941a6"

    def __init__(self, service):
        self.notifying = False
        self.current_index = 0
        self.serialManager = SerialManager()

        Characteristic.__init__(
            self, self.PROCESS_CHARACTERISTIC_UUID,
            ["notify"], service
        )


    # Verify the sendind algorithm
    def send_all_processes(self):
        """Send all processes in one go via notifications."""
        process_data = self.service.get_process_data()
        print("process data -> ", process_data)

        if self.current_index < len(process_data):
            data = process_data[self.current_index]
            self.current_index += 1
            print("Sending: ", data, flush=True)
            value = [dbus.Byte(c.encode()) for c in json.dumps(data)]
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
            return True  # Continue sending
        else:
            print("All processes sent. Sending finish message.", flush=True)

            # Send the "Finished" message to indicate completion
            finish_message = {"status": "Finished"}
            value = [dbus.Byte(c.encode()) for c in json.dumps(finish_message)]
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
            
            print("Finish message sent.", flush=True)
            
            # Optionally clear data after sending the finish message
            self.service.clear_data()  # Uncomment this line to clear data
            
            
            # self.StopNotify()  # Stop notifications (Not needed because user server can notify at multiple times)
            return False  # Stop notifications after finishing


    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        

        self.current_index = 0
        print("Start notify process service", flush=True)

        #TODO: verify if it works, because we have 2 managers, one in each thread
        #serialManager.sendMessage("set_sync")

        self.add_timeout(NOTIFY_TIMEOUT, self.send_all_processes)

        # sys.exit()
        

    def StopNotify(self):
        self.notifying = False
        print("Stop notify process service", flush=True)

# Main entry point
if __name__ == "__main__":
    app = BleApplication()
    app.add_service(ProcessService(0))
    adv = MachineProcessAdvertisement(0)
    app.register()
    adv.register()

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
