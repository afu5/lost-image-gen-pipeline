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
    attitude.txt and filtered_attitude.txt. If not, returns false.'''
def run_LOST_and_filter_once(input_path: str, output_folder: str, database_name: str, 
                            filter: Filter, params: list):
  output_path = output_folder + "/attitude.txt"

  # Run LOST on input_path (pre-transformed image)
  run_lost(input_path, output_path, database_name)

  # Apply filters
  filtered_input_path = output_folder + "/filtered_image.png"
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

  # Check if output files were successfully read
  try: 
    if load_attitude_file(output_path).get("attitude_known") == 0 or \
       load_attitude_file(filtered_output_path).get("attitude_known") == 0:
      print("Attitude is not found")
      return False
  except FileNotFoundError:
    print("Output file not found")
    return False

  return True

''' Compares attitudes given in the two input paths. Returns a dictionary
    of percent error between attitude values for each attitude.'''
def compare_attitudes(attitude_path: str, filtered_attitude_path: str):
  # Read attitude.txt and filtered_attitude.txt
  attitude = load_attitude_file(attitude_path)
  filtered_attitude = load_attitude_file(filtered_attitude_path)
  result = {}
  for attitude_type in attitude:
    percent_error = ((filtered_attitude[attitude_type] - attitude[attitude_type]) 
                      / attitude[attitude_type]) * 100
    result[attitude_type] = percent_error
  return result

''' Loads attitude file given in path, assuming it is formatted like LOST attitude output. Example:
      attitude_known 1
      attitude_ra 17.9868
      attitude_de 63.4233
      attitude_roll 12.238
      attitude_i -0.00786361
      attitude_j -0.5304
      attitude_k 0.0768839
      attitude_real -0.844218 
    Outputs a dictionary mapping attitudes to values as floats.'''
def load_attitude_file(path):
    data = {}
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                key, value = parts
                try:
                    value = float(value)
                except ValueError:
                    pass
                data[key] = value
    return data

# Must be run on a computer that has cloned the LOST repository
if __name__ == "__main__":
  # Make clean and compile LOST (can comment out once run once)
  make_clean_make()

  # Name of output folder and generated database
  output_folder: str = os.path.abspath("output")
  database_name: str = "my-database.dat"

  # Generate database (can comment out once run once)
  generate_database(database_name)

  ''' This code should be in a loop: '''
  # Name of image to process (TODO: Generate the image with LOST, and set constants to match)
  input_path: str = os.path.abspath("input/img_7660.png")

  # Parameters for your filter call (index 0 is the first argument 
  # after img_path and output_path for the method in image_filters.py)
  params = [11, 0]

  result = run_LOST_and_filter_once(input_path, output_folder, database_name, Filter.MOTION_BLUR, params)

  if result:
    # Compare attitudes
    output_path = output_folder + "/attitude.txt"
    filtered_output_path = output_folder + "/filtered_attitude.txt"
    percent_errors = compare_attitudes(output_path, filtered_output_path)

    # Check if any attitude values are more than 5 percent off
    abs_percent_errors = [abs(x) for x in percent_errors.values()]
    highest_percent_error = max(list(abs_percent_errors))
    
    if highest_percent_error > 5:
      print("RESULT: Misidentified attitude for filtered image")
    else:
      print("RESULT: Successfully identified attitude for filtered image")
    
    print("Highest percent error: " + str(highest_percent_error))
  else:
    print("RESULT: Unable to identify attitude for filtered image")
