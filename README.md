# lost-image-gen-pipeline
Pipeline for LOST image generation project. At a high level: 
- Calls LOST to determine attitude of an initial image
- Applies an image transformation (motion blur, noise, random obstruction, etc.) on initial image
- Calls LOST to determine attitude of transformed image
- Compares determined attitudes
