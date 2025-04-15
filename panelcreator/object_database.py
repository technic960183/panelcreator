import numpy as np
import os


class ObjectDatabase:
    _instances = {}

    def __new__(cls, database_path, group_size=None):
        # Ensure that only one instance exists for each unique path
        if database_path in cls._instances:
            # print(f"[WARNING] No new instance created. The instance for {database_path} already exists.")
            return cls._instances[database_path]
        instance = super(ObjectDatabase, cls).__new__(cls)
        cls._instances[database_path] = instance
        return instance

    def __init__(self, database_path):
        # Only initialize if not already initialized
        if not hasattr(self, '_initialized'):
            self.database_path = database_path
            self._image_cube = None
            self._load_data()
            self._initialized = True

    def __len__(self):
        return self._image_cube.shape[0]

    def _load_data(self):
        if os.path.exists(self.database_path):
            self._image_cube = np.load(self.database_path)
        else:
            raise FileNotFoundError(f"File not found: {self.database_path}")

    def get_image(self, index):
        if self._image_cube is None:
            raise ValueError("No data loaded.")
        if index < 0 or index >= len(self):
            raise IndexError("Index out of bounds.")
        return self._image_cube[index]

# Example usage
# db = ObjectDatabase("./working_file/image_cut.npy")
# image = db.get_image(0)
