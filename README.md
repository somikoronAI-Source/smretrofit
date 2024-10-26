# SMRetrofit

SMRetrofit is a Python library designed to process video and image data using machine learning models hosted on the Somikoron API. This library provides functionalities to analyze videos and images, detecting defects and generating ratings based on various criteria.

## Features

- **Video Processing**: Analyze video files frame-by-frame, extract random samples, and save processed frames.
- **Image Processing**: Send image files to the Somikoron API for defect detection and rating.
- **Flexible Modes**: Choose between different modes (`all`, `defect`, `rating`) for tailored outputs.
- **Customizable Parameters**: Adjust font size, thickness, and line spacing for visual annotations.

## Installation

You can install the required packages using pip:
```bash
pip install opencv-python requests Pillow numpy cryptography
```
## Usage

### Initializing the Retrofit Class

To use the SMRetrofit library, you first need to initialize the Retrofit class:
```bash
from smretrofit import Retrofit

# Initialize the Retrofit object
retrofit = Retrofit(auth_key="YOUR_AUTH_KEY", auth_pass="YOUR_AUTH_PASS")
```
### Analyzing a Video

To analyze a video and save the output frames:
```bash
result_data = retrofit.get_video_data_sample("path/to/video.mp4", save=True)
```
### Analyzing an Image

To analyze an image:
```bash
results = retrofit.get_image_data("path/to/image.jpg", save=True)
```
## Parameters

- **url**: API endpoint for Somikoron. Default is "https://api.somikoron.ai/api/".
- **auth_key**: Your authentication key for the API.
- **auth_pass**: Your authentication password for the API.
- **font_size**: Size of the font for labels (default: 7).
- **font_thickness**: Thickness of the font for labels (default: 3).
- **line_space**: Space between lines of labels (default: 10).
- **mode**: Mode of operation (all, defect, rating).

## Example

Here’s a simple example demonstrating how to use the library:
```bash
from smretrofit import Retrofit

# Create an instance of the Retrofit class
retrofit = Retrofit(auth_key="YOUR_AUTH_KEY", auth_pass="YOUR_AUTH_PASS")

# Process a video
result_data = retrofit.get_video_data("path/to/video.mp4", save=True)

# Process an image
results = retrofit.get_image_data("path/to/image.jpg", save=True)
```