from flask import Flask, render_template, Response
from vision.app import Vision
import cv2

app = Flask(__name__)

camera = Vision()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/camera')
def camera_main():
    return render_template('camera.html')


@app.route('/cameramask')
def camera_mask():
    return render_template('cameramask.html')


def gen(camera, *mask):
    camera.run()
    camera.get_frame()

    while True:
        camera.get_frame()
        frame = camera.picture

        if mask:
            frame = camera.picture_mask

        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_mask')
def video_feed_mask():
    return Response(gen(camera, True),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
