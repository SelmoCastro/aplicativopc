import json
import os

class ConfigManager:
    def __init__(self, config_file="settings.json"):
        self.config_file = config_file
        self.default_config = {
            "auto_ram_clean": False,
            "ram_threshold": 80, # Percent per trigger
            "theme": "Dark"
        }
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            return self.default_config.copy()
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except:
            return self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
