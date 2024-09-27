#!/bin/bash

set -e # Exit on error

# Check if NLTK_DATA is set
if [ -z "$NLTK_DATA" ]; then
    echo "NLTK_DATA is not set. Please set it to the path where NLTK data should be downloaded."
    exit 1
fi

mkdir -p ${NLTK_DATA}/corpora ${NLTK_DATA}/models ${NLTK_DATA}/tokenizers

# NLTK data downloads
wget -O ${NLTK_DATA}/corpora/wordnet.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip
wget -O ${NLTK_DATA}/models/word2vec_sample.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/models/word2vec_sample.zip
wget -O ${NLTK_DATA}/corpora/brown.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/brown.zip
wget -O ${NLTK_DATA}/corpora/stopwords.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip
wget -O ${NLTK_DATA}/tokenizers/punkt.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip
wget -O ${NLTK_DATA}/tokenizers/punkt_tab.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip

# Unzip the downloaded NLTK data
unzip ${NLTK_DATA}/corpora/wordnet.zip -d ${NLTK_DATA}/corpora/
unzip ${NLTK_DATA}/models/word2vec_sample.zip -d ${NLTK_DATA}/models/
unzip ${NLTK_DATA}/corpora/brown.zip -d ${NLTK_DATA}/corpora/
unzip ${NLTK_DATA}/corpora/stopwords.zip -d ${NLTK_DATA}/corpora/
unzip ${NLTK_DATA}/tokenizers/punkt.zip -d ${NLTK_DATA}/tokenizers/
unzip ${NLTK_DATA}/tokenizers/punkt_tab.zip -d ${NLTK_DATA}/tokenizers/

# Clean up zip files to reduce image size
rm ${NLTK_DATA}/corpora/*.zip
rm ${NLTK_DATA}/models/*.zip
rm ${NLTK_DATA}/tokenizers/*.zip
