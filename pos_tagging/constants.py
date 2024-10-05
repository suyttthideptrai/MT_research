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
    "vi": "?",
    "zh": "zh_core_web_md",
    "en": "en_core_web_md",
})


