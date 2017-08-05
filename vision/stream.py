from flask import Flask, render_template, Response
from vision.app import Vision
import cv2

app = Flask(__name__)

camera = Vision()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cameraBack')
def camera_back():
    return 'Hello, World!'


def gen(camera):
    camera.run()

    while True:
        camera.get_frame()
        frame = camera.picture
        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
