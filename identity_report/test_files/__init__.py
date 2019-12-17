import os

test_data_dir = os.path.dirname(__file__)

test_files = [f for f in os.listdir(test_data_dir) if os.path.isfile(os.path.join(test_data_dir, f)) and (os.path.basename(f) != '__init__.py' and os.path.basename(f) != '.DS_Store')]
