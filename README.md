# Lost Image Gen Pipeline
This is a pipeline for HSL's [LOST](https://github.com/UWCubeSat/lost) image generation project. Our objective is to build a pipeline that can be used for testing how suboptimal image conditions (motion blur, noise, random obstruction, etc.) affect the accuracy of our star tracker. At a high level, this pipeline: 
- Calls LOST to determine attitude of an initial image
- Applies an image transformation on initial image
- Calls LOST to determine attitude of transformed image
- Compares determined attitudes to see if filtered image has been successfully identified within a percent error of the unfiltered image

### Instructions for running: 
Make sure you have run `git clone` for the LOST directory somewhere on your device. `git clone` this repository. Make sure the calls to `make_clean_make()` and `generate_database` in `main.py`'s main method are not commented out during your first run (you can comment them out in later runs for efficiency), and run `python3 main.py`. 