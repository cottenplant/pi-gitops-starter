# Multi-stage arm64-friendly build: uv resolves everything, no apt layer.
# SKELETON: unvalidated draft — build and boot this for real at v1.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ src/
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm
WORKDIR /app
COPY --from=build /app/.venv .venv/
COPY --from=build /app/src src/
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["python", "-m", "example_app"]
