import os
import subprocess
from image_filters import motion_blur

LOST_DIR = os.path.abspath("../lost")
LOST = os.path.join(LOST_DIR, "lost")

FOCAL_LENGTH = 49
PIXEL_SIZE = 22.2
CENTROID_MAG_FILTER = 5

ANGULAR_TOLERANCE = 0.05
FALSE_STARS = 1000
MAX_MISMATCH_PROB = 0.0001

if __name__ == "__main__":
  # Name of image to process
  input_path: str = os.path.abspath("img_7660.png")

  # Name of output attitude file and generated database
  output_path: str = os.path.abspath("attitude.txt")
  database_name: str = "my-database.dat"

  # Make clean and make
  # subprocess.run(args=["make", "clean"], cwd=LOST_DIR)
  # subprocess.run(args=["make"], cwd=LOST_DIR)

  # Generate database
  subprocess.run(args=[LOST, "database",
                        "--max-stars", str(5000),
                        "--kvector",
                        "--kvector-min-distance", str(0.2),
                        "--kvector-max-distance", str(15),
                        "--kvector-distance-bins", str(10000),
                        "--output", database_name
                      ], cwd=LOST_DIR)

  # Run LOST on input_name
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
  
  # Apply filters (TODO: add customization flags to determine what is called)
  filtered_input_path = os.path.abspath("filtered_image.png")
  filtered_output_path = os.path.abspath("filtered_attitude.txt")
  motion_blur(input_path, filtered_input_path, 10)

  # Run lost on filtered input
  subprocess.run(args=[LOST, "pipeline",
                       "--png", filtered_input_path, 
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
                       "--print-attitude", filtered_output_path
                       ], cwd=LOST_DIR)

  try: 
    with open(output_path, "r") as file: 
      attitude = file.read()
      print(attitude)
  except FileNotFoundError:
    print(output_path + " not found")

  try: 
    with open(filtered_output_path, "r") as file: 
      attitude = file.read()
      print(attitude)
  except FileNotFoundError:
    print(filtered_output_path + " not found")
