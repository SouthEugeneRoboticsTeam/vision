FROM valian/docker-python-opencv-ffmpeg:py3

ADD cameras app/cameras
ADD config app/config
ADD tests app/tests
ADD vision app/vision
ADD run.py app/run.py
ADD requirements.txt app/requirements.txt

WORKDIR app

RUN pip3 install -r requirements.txt

CMD python3 run.py
