import spacy
import os
import sys
import concurrent.futures
import constants as const

from utils import read_file, write_pos_tagged_file, read_cached_batch_size

nlp = spacy.blank("en")
vi_flag = False
vi_tag_mapping = {
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


def load_model(language_id):
    global nlp
    spacy.blank(language_id)
    cache_dir = const.MODEL_CACHE_DIR
    model_name = str(const.SPACY_TAGGING_MODELS[language_id])
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    print("Tagging model: " + model_name)
    print("Loading model ...")
    try:
        nlp = spacy.load(os.path.join(cache_dir, model_name))
    except OSError:
        print("Model not initialized. Downloading model: " + model_name + "...")
        if language_id == "vi":
            # model_path = str(const.THIRD_PARTY_MODEL_PATHS[language_id])
            # spacy.cli.download(model_path)
            nlp = spacy.load(model_name)
            nlp.to_disk(os.path.join(cache_dir, model_name))
        else:
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name)
            nlp.to_disk(os.path.join(cache_dir, model_name))

def pos_tag_sentences(sentences, _batch_size):
    global vi_flag, vi_tag_mapping
    # pos_sentences = []
    tag_sentences = []
    sentences_len = len(sentences)
    log_num = const.LOG_PER_NUMBER_OF_LINE_TAGGING

    # Batch processing with nlp.pipe
    # for i, doc in enumerate(nlp.pipe(sentences, batch_size=_batch_size)):
    for i, doc in enumerate(nlp.pipe(sentences)):
        # Print progress every 100 sentences to reduce logging overhead
        if  log_num >= sentences_len - i:
            sys.stdout.write(f"\rNumber Of Sentences Processed: {i + 1}/{sentences_len}")
            sys.stdout.flush()
        if i % log_num == 0:
            sys.stdout.write(f"\rNumber Of Sentences Processed: {i}/{sentences_len}")
            sys.stdout.flush()
        # pos_processed_sentence = " ".join([token.pos_ for token in doc])
        if vi_flag:
            tag_processed_sentence = " ".join([map_tag_to_new_format(token.tag_) for token in doc])
        else:
            tag_processed_sentence = " ".join([token.tag_ for token in doc])
        # pos_sentences.append(pos_processed_sentence)
        tag_sentences.append(tag_processed_sentence)

    return tag_sentences


#process tagging
def process(source_file_path, result_file_name, language_id, batch_size_, core_num):
    global nlp, vi_flag
    nlp = spacy.blank(language_id)
    if language_id == "vi":
        vi_flag = True
    #disable unnecessary pipes
    print("Available pipes: ", nlp.pipe_names)
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in const.ALLOWED_PIPE_NAMES_LIKE]
    print("Disabling pipes: ", other_pipes)
    nlp.disable_pipes(*other_pipes)
    sentences = read_file(source_file_path)
    print("File's number of rows: " + str(len(sentences)))
    # device_compatible_batch_size = read_cached_batch_size()
    load_model(language_id)
    processed_sentences = pos_tag_sentences(sentences, batch_size_)
    write_pos_tagged_file(processed_sentences, result_file_name)

# def process_batch(sentences, _batch_size):
#     pos_sentences, tag_sentences = pos_tag_sentences(sentences, _batch_size)
#     return pos_sentences, tag_sentences
# with concurrent.futures.ProcessPoolExecutor() as executor:
#     chunks = read_in_chunks('your_file.txt', chunk_size=20000)
#     results = executor.map(lambda chunk: process_batch(chunk, _batch_size), chunks)
#
# def read_in_chunks(file, chunk_size=10000):
#     with open(file, 'r') as f:
#         while True:
#             lines = list(itertools.islice(f, chunk_size))
#             if not lines:
#                 break
#             yield lines


def map_tag_to_new_format(tag):
    return vi_tag_mapping.get(tag, 'X')  # Defaults to 'X' if tag is not found
