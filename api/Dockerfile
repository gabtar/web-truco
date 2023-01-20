FROM python:3.10-alpine
WORKDIR /app
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
EXPOSE 80
