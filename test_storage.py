from storage_manager import StorageManager

data = {
    "pure": 1000,
    "silkcut": 0,
    # "discolored": 0,
    "broken": 0,
    "unknown": 0
}

storage_manager = StorageManager(data)
storage_manager.insert_data()
