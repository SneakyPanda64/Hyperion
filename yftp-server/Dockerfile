FROM python:3.10-alpine
ENV PYTHONUNBUFFERED 1

COPY . ./home
WORKDIR /home
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk update
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python -m venv /opt/venv
RUN pip3 install -r requirements.txt
EXPOSE 21

CMD ["python3", "main.py"]