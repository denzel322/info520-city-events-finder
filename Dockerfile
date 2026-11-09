FROM python:3.12-slim
WORKDIR /app
COPY app.py index.html app.js style.css ./
RUN useradd --uid 10001 --create-home appuser
USER appuser
ENV PORT=8080 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "app.py"]
