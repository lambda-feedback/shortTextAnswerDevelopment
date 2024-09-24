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

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip 

#  ----- For Linux development
# # Warnings: those commands sometimes download corrupted zips, so it is better to wget each package from the main site
# RUN python -m nltk.downloader wordnet
# RUN python -m nltk.downloader word2vec_sample
# RUN python -m nltk.downloader brown
# RUN python -m nltk.downloader stopwords
# RUN python -m nltk.downloader punkt
# RUN python -m nltk.downloader punkt_tab

#  ----- For MaxOS development
RUN mkdir -p /usr/share/nltk_data/corpora /usr/share/nltk_data/models /usr/share/nltk_data/tokenizers
RUN mkdir -p /app/evaluation_function/models

# NLTK data downloads
RUN wget -O /usr/share/nltk_data/corpora/wordnet.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip
RUN wget -O /usr/share/nltk_data/models/word2vec_sample.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/models/word2vec_sample.zip
RUN wget -O /usr/share/nltk_data/corpora/brown.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/brown.zip
RUN wget -O /usr/share/nltk_data/corpora/stopwords.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip
RUN wget -O /usr/share/nltk_data/tokenizers/punkt.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip
RUN wget -O /usr/share/nltk_data/tokenizers/punkt_tab.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip

# Unzip the downloaded NLTK data
RUN unzip /usr/share/nltk_data/corpora/wordnet.zip -d /usr/share/nltk_data/corpora/
RUN unzip /usr/share/nltk_data/models/word2vec_sample.zip -d /usr/share/nltk_data/models/
RUN unzip /usr/share/nltk_data/corpora/brown.zip -d /usr/share/nltk_data/corpora/
RUN unzip /usr/share/nltk_data/corpora/stopwords.zip -d /usr/share/nltk_data/corpora/
RUN unzip /usr/share/nltk_data/tokenizers/punkt.zip -d /usr/share/nltk_data/tokenizers/
RUN unzip /usr/share/nltk_data/tokenizers/punkt_tab.zip -d /usr/share/nltk_data/tokenizers/

# Clean up zip files to reduce image size
RUN rm /usr/share/nltk_data/corpora/*.zip
RUN rm /usr/share/nltk_data/models/*.zip
RUN rm /usr/share/nltk_data/tokenizers/*.zip

RUN wget -O /app/evaluation_function/models/Phi-3.5-mini-instruct-Q6_K.gguf https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q6_K.gguf

# Layer 3: Final image
FROM ghcr.io/lambda-feedback/evaluation-function-base/python:3.11

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

ENV NLTK_DATA=/usr/share/nltk_data \
    PATH="/usr/share/nltk_data:$PATH"

ENV MODEL_PATH=/app/evaluation_function/models \
    PATH="/app/evaluation_function/models:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=models ${NLTK_DATA} ${NLTK_DATA}
COPY --from=models ${MODEL_PATH} ${MODEL_PATH}

# Precompile python files for faster startup
RUN python -m compileall -q .

# Copy the evaluation function to the app directory
COPY evaluation_function ./evaluation_function

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