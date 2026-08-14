FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /srv

COPY pyproject.toml .
COPY src ./src
COPY fixtures ./fixtures

# Se instala tambien el extra de OpenAI para poder pasar de generacion
# determinista a LLM con solo cambiar AI_ENGINE_GENERATOR, sin reconstruir.
RUN pip install --no-cache-dir -e ".[openai]"

# El motor escucha en 127.0.0.1 por defecto: dentro del contenedor hace falta 0.0.0.0.
ENV AI_ENGINE_HOST=0.0.0.0 AI_ENGINE_PORT=8000

EXPOSE 8000
CMD ["ai-engine-api"]
