FROM python:3.10

WORKDIR /app

RUN pip install debugpy

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
COPY ./requirements.txt $WORKDIR
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000 5678

# Start with debugpy
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]