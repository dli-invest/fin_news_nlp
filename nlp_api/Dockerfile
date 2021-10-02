FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
ENV APP_MODULE app.api:app
ENV LOG_LEVEL debug
ENV WEB_CONCURRENCY 2

# Install spacy requirments separately first so that Docker will 
# cache the (somewhat) expensive download of a spacy model
COPY ./requirements/spacy.txt ./requirements/spacy.txt
RUN pip install -r requirements/spacy.txt
RUN spacy download en_core_web_sm

COPY ./requirements/base.txt ./requirements/base.txt
RUN pip install -r requirements/base.txt

# COPY .env /app/.env
COPY ./app /app/app

EXPOSE 8000 
ENTRYPOINT [ "python" ] 
CMD [ "main.py" ] 