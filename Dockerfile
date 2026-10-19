FROM python:3.14-bookworm AS uv

COPY --from=ghcr.io/astral-sh/uv:0.12.11 /uv /uvx /bin/

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN \
  --mount=type=cache,target=/var/lib/apt/lists \
  --mount=type=cache,target=/var/cache/apt/archives \
  apt-get update \
  && apt-get install -y --no-install-recommends build-essential

# Download dependencies as a separate step to take advantage of Docker's caching.
# Bind the project metadata without copying application sources into this layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --locked --no-install-project

FROM uv AS run

# # Create a non-privileged user that the app will run under.
# # See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
# ARG UID=10001
# RUN adduser \
#     --disabled-password \
#     --gecos "" \
#     --home "/nonexistent" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     appuser

# # Switch to the non-privileged user to run the application.
# USER appuser

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked

EXPOSE ${PORT}

CMD [".venv/bin/python", "-m", "streamlit", "run", "app/main.py", "--browser.serverAddress", "0.0.0.0"]
