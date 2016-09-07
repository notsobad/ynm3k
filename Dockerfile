FROM python:2.7
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
ADD . /code
EXPOSE 9527
CMD python ynm3k.py
