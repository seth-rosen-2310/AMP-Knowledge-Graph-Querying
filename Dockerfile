FROM python:3.10.13-bookworm

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV API_KEY ""
ENV GRAPH_USER ""
ENV GRAPH_PASSWORD ""

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]