#!/usr/bin/env python

from vision.app import Vision
from vision import args
import vision.stream as stream

video_stream = args['stream']
app = Vision()

print video_stream
if video_stream is not None:
    app.run()
    # stream

else:
    app.run()
