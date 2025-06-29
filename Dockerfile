FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copies the whole app 
COPY . . 

CMD ["python", "main.py"]