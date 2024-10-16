import os
from types import MappingProxyType

SPACY_MODEL_NAME_EN = "en_core_web_md"
ALLOWED_PIPE_NAMES_LIKE = ["tagger", "tok2vec", "attribute_ruler"]
LOG_PER_NUMBER_OF_LINE_TAGGING = 100
MODEL_CACHE_DIR = os.getenv("cache_dir", "../../models")
MAX_MEMORY_USAGE_RATIO = 0.5
INITIAL_TAGGING_BATCH_SIZE = 200
DEFAULT_TAGGING_BATCH_SIZE = 1000
DEFAULT_TAGGING_CORE_NUM = 1
CACHE_ENV_VAR = "SPACY_BATCH_SIZE"

POS_OUTPUT_POSTFIX = ".pos"
TAG_OUTPUT_POSTFIX = ".tag"

ALLOWED_LANGUAGE_IDS = ["vi", "zh", "en"]

SPACY_TAGGING_MODELS = MappingProxyType({
    "vi": "vi_core_news_lg",
    "zh": "zh_core_web_md",
    "en": "en_core_web_md",
})

THIRD_PARTY_MODEL_PATHS = MappingProxyType({
    "vi": "https://gitlab.com/trungtv/vi_spacy/-/raw/master/vi_core_news_lg/dist/vi_core_news_lg-0.0.1.tar.gz"
})


VI_TAG_MAPPING = {
    'A': 'ADJ',            # Adjective
    'C': 'CCONJ',          # Coordinating conjunction
    'E': 'ADP',            # Preposition
    'I': 'INTJ',           # Interjection
    'L': 'DET',            # Determiner
    'M': 'NUM',            # Numeral
    'N': 'NOUN',           # Common noun
    'Nc': 'NOUN',          # Noun classifier
    'Ny': 'NOUN',          # Noun abbreviation
    'Np': 'PROPN',         # Proper noun
    'Nu': 'NUM',           # Unit noun
    'P': 'PRON',           # Pronoun
    'R': 'ADV',            # Adverb
    'S': 'SCONJ',          # Subordinating conjunction
    'T': 'AUX',            # Auxiliary, modal words
    'V': 'VERB',           # Verb
    'X': 'X',              # Unknown
    'F': 'PUNCT',          # Filtered out (punctuation)
}

SRC_COLUMN_NAME = 'Source'
TGT_COLUMN_NAME = 'Target'
CORPUS_COLUMN_NAME = 'Label'

DEFAULT_DEV_ROW = 2000
DEFAULT_TEST_ROW = 2000