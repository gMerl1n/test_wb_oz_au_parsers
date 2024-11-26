FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /wb_oz_au_parsers

WORKDIR /wb_oz_au_parsers

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8092

ENV PYTHONPATH "${PYTHONPATH}:/usr/local/wb_oz_au_parsers/"

RUN chmod a+x /wb_oz_au_parsers/start.sh

ENTRYPOINT ["./start.sh"]