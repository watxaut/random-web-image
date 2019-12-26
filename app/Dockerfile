FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ADD requirements.txt /app/

RUN pip3 install -r requirements.txt

ADD ./ /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--proxy-headers"]
