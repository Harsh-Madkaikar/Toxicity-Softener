import os, subprocess, sys
base = os.path.dirname(os.path.abspath(__file__))
subprocess.check_call([sys.executable, os.path.join(base, "data", "make_large_dataset.py")])
subprocess.check_call([sys.executable, os.path.join(base, "nlp", "classifier.py")])
