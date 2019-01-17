FROM valian/docker-python-opencv-ffmpeg

ADD config app/config
ADD tests app/tests
ADD vision app/vision
ADD run.py app/run.py
ADD requirements.txt app/requirements.txt

WORKDIR app

RUN pip install -r requirements.txt

CMD python run.py
