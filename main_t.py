import unittest
import os

class CustomTestLoader(unittest.TestLoader):
    def _match_path(self, path, full_path, pattern):
        # Exclude main_t.py
        if os.path.basename(path) == 'main_t.py':
            return False
        return super()._match_path(path, full_path, pattern)

if __name__ == '__main__':
    loader = CustomTestLoader()
    suite = loader.discover(start_dir='.', pattern='*_t.py')

    runner = unittest.TextTestRunner()
    runner.run(suite)