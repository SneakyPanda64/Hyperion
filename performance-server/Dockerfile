FROM pytorch/pytorch:latest
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /home
WORKDIR /home
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get -y update && apt-get install -y libsndfile1
RUN apt install -y git
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python -m venv /opt/venv

RUN pip3 install torchaudio --extra-index-url https://download.pytorch.org/whl/cu116 --no-cache-dir
RUN pip install -r requirements.txt

# Enable venv
CMD ["python3", "main.py"]