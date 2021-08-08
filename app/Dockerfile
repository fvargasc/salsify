FROM python

COPY . /app

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV INPUT_FILES_DIRECTORY=/input_files

CMD python /app/line_index.py && gunicorn --bind 0.0.0.0:5000 --workers=8 --threads 16 --backlog 2048 wsgi:app
