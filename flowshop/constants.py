import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

RANDOM_SEED = 42
DEFAULT_TRIALS = 100
DEFAULT_N_JOBS = 10
DEFAULT_LOW = 1
DEFAULT_HIGH = 20