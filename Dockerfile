FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:/root/.local/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      imagemagick \
      ghostscript \
      qpdf \
      poppler-utils \
      libimage-exiftool-perl \
      icc-profiles-free \
      file \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY tests ./tests
COPY examples ./examples
COPY scripts ./scripts

RUN chmod +x scripts/check_prepress_tools.sh \
    && uv sync --extra dev \
    && uv run pytest -q \
    && scripts/check_prepress_tools.sh

VOLUME ["/app/print_jobs"]
ENTRYPOINT ["uv", "run", "ai-print-ready"]
CMD ["--help"]
