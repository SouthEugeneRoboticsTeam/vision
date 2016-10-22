# SERT Vision

![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)
![License](https://img.shields.io/github/license/andrewda/robotics-vision.svg)

SERT's OpenCV vision code.

## Usage

Before starting the program, you must install OpenCV v2.4.x along with the
pip dependencies:

```bash
$ pip install -r requirements.txt
```

Then, you can run the program using

```bash
$ python app.py
```

## Configuration

All command-line arguments may be configured in the `config.ini` file
(located at `config/config.ini`). For example, the `--lower-rgb`
argument may be edited using the `lower-rgb` line in the `config.ini`.

```
-h, --help            show this help message and exit
-i IMAGE, --image IMAGE
					  path to image [env var: VISION_IMAGE]
-ma MIN_AREA, --min-area MIN_AREA
					  minimum area for blobs [env var: VISION_MIN_AREA]
-lt LOWER_RGB, --lower-rgb LOWER_RGB
					  lower threshold for RGB values [env var: VISION_LOWER_RGB]
-ut UPPER_RGB, --upper-rgb UPPER_RGB
					  upper threshold RGB values [env var: VISION_UPPER_RGB]
```
