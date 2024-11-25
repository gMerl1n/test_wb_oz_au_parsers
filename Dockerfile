FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN mkdir /wb_oz_au_parsers

WORKDIR /wb_oz_au_parsers

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod a+x /wb_oz_au_parsers/start.sh

ENTRYPOINT ["./start.sh"]