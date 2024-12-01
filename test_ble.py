import os
import subprocess
import threading
from gatt_server_manager import BleApplication, MachineProcessAdvertisement, ProcessService
import time  # For sleeping in the loop to periodically check the stop event

def fetchIpAddress():
    command = 'hostname -I'
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc = proc.communicate()[0]
    ip_address = str(proc).split(" ")[0].split('\'')[1]

    print("GATT application IP address: %s" % ip_address, flush=True)

def run_ble_app(stop_event):
    # Run the BLE application in a separate thread
    ble_app = BleApplication()
    ble_app.add_service(ProcessService(0))
    ble_app.register()

    ble_adv = MachineProcessAdvertisement(0)
    ble_adv.register()

    print('Starting BLE application...')
    fetchIpAddress()

    try:
        while not stop_event.is_set():
            # Add a small delay to allow the event to be checked periodically
            time.sleep(1)  # Adjust the sleep duration if necessary

            # Simulate running BLE application by checking if the event is set
            # Note: You may need to adjust this depending on how `ble_app.run()` works.
            ble_app.run()

    except Exception as e:
        print(f"Error while running BLE: {e}")

    finally:
        ble_app.quit()  # Ensure the BLE application is stopped when the thread ends
        print("BLE application stopped.")

def main():
    stop_event = threading.Event()  # Event to control stopping BLE app

    print('Type "start" to begin the BLE application, "stop" to quit.')

    while True:
        user_input = input("Enter command: ").strip().lower()  # Read input and handle case-insensitive
        
        if user_input == 'start':
            # Start BLE in a new thread
            ble_thread = threading.Thread(target=run_ble_app, args=(stop_event,), daemon=True)
            ble_thread.start()
            print("BLE application is running in a separate thread.")
        
        elif user_input == 'stop':
            # Set the stop event to signal the BLE thread to stop
            print('Stopping BLE application...')
            stop_event.set()  # This will stop the BLE application
            break  # Exit the loop when stop is typed
            
        else:
            print('Invalid command. Type "start" to begin or "stop" to quit.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
        pass
