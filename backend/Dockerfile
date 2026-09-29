FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py model.json ./
RUN useradd --create-home app
USER app
# PORT est imposé par certains hébergeurs (Render, Cloud Run…)
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
