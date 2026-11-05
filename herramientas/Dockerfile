FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Europe/Madrid \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /repo/herramientas

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

# El punto de entrada es python3: así "docker compose run --rm herramientas
# generar.py --empresa cerveceria --alumno 07" ejecuta ese script.
ENTRYPOINT ["python3"]
CMD ["-c", "print('Servicio de herramientas. Uso: docker compose run --rm herramientas <script> --ayuda')"]
