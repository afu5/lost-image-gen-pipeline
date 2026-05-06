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

''' input_path is the path to your input image. output_folder is the folder for the generated
    attitude.txt files. database_name is the name of your already-generated database. filter is
    the Filter enum for the filter you want to use. params is an array of the remaining
    parameters that your filter requires to be run (check image_filters.py).
    
    If successful, produces two output attitude files in your output_path folder,
    attitude.txt and filtered_attitude.txt. If not, throws a FileNotFoundError.'''
def run_LOST_and_filter_once(input_path: str, output_folder: str, database_name: str, 
                            filter: Filter, params: list):
  output_path = output_folder + "/attitude.txt"

  # Run LOST on input_path (pre-transformed image)
  run_lost(input_path, output_path, database_name)

  # Apply filters
  filtered_input_path = output_folder + "/filtered_image.png"
  print(filtered_input_path)
  filtered_output_path = output_folder + "/filtered_attitude.txt"

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
    return

  # Run lost on filtered_input_path
  run_lost(filtered_input_path, filtered_output_path, database_name)

def compare_attitudes(attitude_path: str, filtered_attitude_path: str):
  # Read attitude.txt and filtered_attitude.txt
  try: 
    with open(attitude_path, "r") as result, open(filtered_attitude_path, "r") as filtered_result:  
      attitude = result.read()
      filtered_attitude = filtered_result.read()
      print(attitude)
      print(filtered_attitude)
  except FileNotFoundError:
    print(attitude_path + " not found")

# Must be run on a computer that has cloned the LOST repository
if __name__ == "__main__":
  # Make clean and compile LOST (can comment out once run once)
  make_clean_make()

  # Name of output folder and generated database
  output_folder: str = os.path.abspath("output")
  database_name: str = "my-database.dat"

  # Generate database
  generate_database(database_name)

  '''This code should be in a loop: '''
  # Name of image to process (TODO: Generate the image with LOST, and set constants to match)
  input_path: str = os.path.abspath("input/img_7660.png")

  # Parameters for your filter call (index 0 is the first argument 
  # after img_path and output_path for the method in image_filters.py)
  params = [15, 0]

  run_LOST_and_filter_once(input_path, output_folder, database_name, Filter.MOTION_BLUR, params)

  output_path = output_folder + "/attitude.txt"
  filtered_output_path = output_folder + "/filtered_attitude.txt"
  compare_attitudes(output_path, filtered_output_path)
