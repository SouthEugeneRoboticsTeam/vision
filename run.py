#!/usr/bin/env python

from vision.app import Vision
from vision import args
import vision.stream as stream

video_stream = args['stream']
app = Vision()

if not video_stream:
    app.run()

else:
    stream.app.run()
