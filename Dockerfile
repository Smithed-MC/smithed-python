FROM python:3.11-bookworm as rye

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH="/app/src:$PYTHONPATH"

WORKDIR /app

RUN \
  --mount=type=cache,target=/var/lib/apt/lists \
  --mount=type=cache,target=/var/cache/apt/archives \
  apt-get update \
  && apt-get install -y --no-install-recommends build-essential

ENV RYE_HOME="/opt/rye"
ENV PATH="$RYE_HOME/shims:$PATH"

# RYE_INSTALL_OPTION is required to build.
# See: https://github.com/mitsuhiko/rye/issues/246
RUN curl -sSf https://rye-up.com/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a bind mount to some files to avoid having to copy them into
# into this layer.
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=requirements.lock,target=requirements.lock \
    --mount=type=bind,source=requirements-dev.lock,target=requirements-dev.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    --mount=type=bind,source=README.md,target=README.md \
    rye sync --no-lock

RUN . .venv/bin/activate

FROM rye AS run

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Switch to the non-privileged user to run the application.
USER appuser

COPY . .

EXPOSE ${PORT}

CMD ["rye", "run", "streamlit", "run", "app/main.py", "--browser.serverAddress", "0.0.0.0"]
