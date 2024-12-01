import json
from datetime import datetime

class StorageManager:
    def __init__(self, data):
        self.data = data
        self.file_path = "processes_store.json"
    
    def _read_json(self):
        """Reads the existing JSON file and returns the data."""
        with open(self.file_path, 'r') as file:
            return json.load(file)
    
    def _write_json(self, data):
        """Writes the updated data back to the JSON file."""
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)
    
    def _generate_timestamp(self):
        """Generates a timestamp in the format '2024-11-18T15:45:00Z'."""
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _generate_process_id(self):
        """Generates a unique process ID based on the current number of processes."""
        json_data = self._read_json()
        process_id = f"Process_{len(json_data['processes']) + 1:03}"
        return process_id
    
    def insert_data(self):
        """Inserts the data into the JSON file."""
        json_data = self._read_json()

        # Generate the process ID and timestamp
        timestamp = self._generate_timestamp()
        process_id = self._generate_process_id()

        # Prepare the new process entry
        new_process = {
            "processId": process_id,
            "classificationSummary": {
                "Pure": self.data["pure"],
                "Broken": self.data["broken"],
                # "Discolored": self.data["discolored"],
                "Silkcut": self.data["silkcut"],
                "Unknown": self.data["unknown"]
            },
            "timestamp": timestamp
        }

        # Append the new process to the processes array
        json_data["processes"].append(new_process)

        # Write the updated data back to the file
        self._write_json(json_data)

        print(f"Process {process_id} added successfully.")
