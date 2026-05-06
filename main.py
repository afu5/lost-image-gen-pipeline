import os
import subprocess
from image_filters import Filter, motion_blur, dark_current_noise_generator

LOST_DIR = os.path.abspath("../lost")
LOST = os.path.join(LOST_DIR, "lost")

# Current values determined by the LOST README commands
# Generating database

MAX_STARS = 5000
KVECTOR_MIN_DISTANCE = 0.2
KVECTOR_MAX_DISTANCE = 15
KVECTOR_DISTANCE_BINS = 10000

# Running LOST for img_7660.png
FOCAL_LENGTH = 49
PIXEL_SIZE = 22.2
CENTROID_MAG_FILTER = 5
ANGULAR_TOLERANCE = 0.05
FALSE_STARS = 1000
MAX_MISMATCH_PROB = 0.0001

def generate_database(database_name: str): 
  subprocess.run(args=[LOST, "database",
                        "--max-stars", str(MAX_STARS),
                        "--kvector",
                        "--kvector-min-distance", str(KVECTOR_MIN_DISTANCE),
                        "--kvector-max-distance", str(KVECTOR_MAX_DISTANCE),
                        "--kvector-distance-bins", str(KVECTOR_DISTANCE_BINS),
                        "--output", database_name
                      ], cwd=LOST_DIR)

def run_lost(input_path: str, output_path: str, database_name: str):
  subprocess.run(args=[LOST, "pipeline",
                      "--png", input_path, 
                      "--focal-length", str(FOCAL_LENGTH), 
                      "--pixel-size", str(PIXEL_SIZE), 
                      "--centroid-algo", "cog",
                      "--centroid-mag-filter", str(CENTROID_MAG_FILTER),
                      "--database", database_name,
                      "--star-id-algo", "py",
                      "--angular-tolerance", str(ANGULAR_TOLERANCE),
                      "--false-stars", str(FALSE_STARS),
                      "--max-mismatch-prob", str(MAX_MISMATCH_PROB),
                      "--attitude-algo", "dqm",
                      "--print-attitude", output_path
                      ], cwd=LOST_DIR)
  
def make_clean_make():
  # Make clean and make
  subprocess.run(args=["make", "clean"], cwd=LOST_DIR)
  subprocess.run(args=["make"], cwd=LOST_DIR)

''' input_path is the path to your input image. output_path is the path for the generated
    attitude.txt. database_name is the name of your already-generated database. filter is
    the Filter enum for the filter you want to use. params is an array of the remaining
    parameters that your filter requires to be run (check image_filters.py).'''
def run_LOST_and_filter_once(input_path: str, output_path: str, database_name: str, 
                            filter: Filter, params):
  # Run LOST on input_path
  run_lost(input_path, output_path, database_name)

  # Apply filters (TODO: add customization flags to determine what is called)
  filtered_input_path = os.path.abspath("output/filtered_image.png")
  filtered_output_path = os.path.abspath("output/filtered_attitude.txt")

  if filter == Filter.BRIGHT_OBSTRUCTION:
    print("Not yet implemented!")
    return
  elif filter == Filter.MOTION_BLUR:
    motion_blur(input_path, filtered_input_path, params[0], params[1])
  elif filter == Filter.DARK_CURRENT_NOISE:
    dark_current_noise_generator(input_path, filtered_input_path, params[0], 
                                 params[1], params[2], params[3])
  else:
    print("Invalid Filter parameter in run_pipeline_once")

  # Run lost on filtered_input_path
  run_lost(filtered_input_path, filtered_output_path)

  # Read attitude.txt
  try: 
    with open(output_path, "r") as file: 
      attitude = file.read()
      print(attitude)
  except FileNotFoundError:
    print(output_path + " not found")

  # Read filtered_attitude.txt
  try: 
    with open(filtered_output_path, "r") as file: 
      attitude = file.read()
      print(attitude)
  except FileNotFoundError:
    print(filtered_output_path + " not found")

# Must be run on a computer that has cloned the LOST repository
if __name__ == "__main__":
  # Make clean and compile LOST
  make_clean_make()

  # Name of image to process
  input_path: str = os.path.abspath("input/img_7660.png")

  # Name of output attitude file and generated database
  output_path: str = os.path.abspath("output/attitude.txt")
  database_name: str = "my-database.dat"

  # Generate database
  generate_database(database_name)

  # Create parameters for your filter call (index 0 is the first argument 
  # after input_path and output_path)
  params = [15, 0]

  run_LOST_and_filter_once(input_path, output_path, database_name, Filter.MOTION_BLUR, params)
