# Layer 1: Build the virtual environment
FROM ghcr.io/lambda-feedback/evaluation-function-base/python:3.11 AS builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml ./
RUN poetry lock

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --without dev --no-root

# Layer 2: Download NLTK models
FROM ghcr.io/lambda-feedback/evaluation-function-base/python:3.11 AS models

ENV NLTK_DATA=/usr/share/nltk_data

ENV MODEL_PATH=/app/evaluation_function/models

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip

COPY ./scripts ./scripts

RUN ./scripts/download_models.sh
RUN ./scripts/download_nltk.sh

# Layer 3: Final image
FROM ghcr.io/lambda-feedback/evaluation-function-base/python:3.11

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

ENV NLTK_DATA=/usr/share/nltk_data

ENV MODEL_PATH=/app/evaluation_function/models

# Copy the evaluation function to the app directory
COPY ./evaluation_function ./evaluation_function

# Precompile python files for faster startup
RUN python -m compileall -q .

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=models ${NLTK_DATA} ${NLTK_DATA}
COPY --from=models ${MODEL_PATH} ${MODEL_PATH}

#  ----- For Linux development instead of Layer 2 NLTK downloads
# # Warnings: those commands sometimes download corrupted zips, so it is better to wget each package from the main site
# RUN python -m nltk.downloader wordnet
# RUN python -m nltk.downloader word2vec_sample
# RUN python -m nltk.downloader brown
# RUN python -m nltk.downloader stopwords
# RUN python -m nltk.downloader punkt
# RUN python -m nltk.downloader punkt_tab

ENV EVAL_RPC_TRANSPORT="ipc"

# Command to start the evaluation function with
ENV FUNCTION_COMMAND="python"

# Args to start the evaluation function with
ENV FUNCTION_ARGS="-m,evaluation_function.main"

# The transport to use for the RPC server
ENV FUNCTION_RPC_TRANSPORT="ipc"

ENV LOG_LEVEL="debug"

# ------- FOR DEBIAN
# Keep the container running
# CMD ["tail", "-f", "/dev/null"]