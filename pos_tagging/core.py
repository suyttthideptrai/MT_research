import spacy
import os
import sys
import concurrent.futures
import constants as const

from utils import read_file, write_pos_tagged_file, read_cached_batch_size

nlp = spacy.blank("en")

def load_model(language_id):
    global nlp
    spacy.blank(language_id)
    cache_dir = const.MODEL_CACHE_DIR
    model_path = str(const.SPACY_TAGGING_MODELS[language_id])
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    print("Tagging model: " + model_path)
    print("Loading model ...")
    try:
        nlp = spacy.load(os.path.join(cache_dir, model_path))
    except OSError:
        print("Model not initialized. Downloading model: " + model_path + "...")
        spacy.cli.download(model_path)
        nlp = spacy.load(model_path)
        nlp.to_disk(os.path.join(cache_dir, model_path))

def pos_tag_sentences(sentences, _batch_size):
    pos_sentences = []
    tag_sentences = []
    sentences_len = len(sentences)
    log_num = const.LOG_PER_NUMBER_OF_LINE_TAGGING
    # Batch processing with nlp.pipe
    for i, doc in enumerate(nlp.pipe(sentences, batch_size=_batch_size)):
        # Print progress every 100 sentences to reduce logging overhead
        if  log_num >= sentences_len - i:
            sys.stdout.write(f"\rNumber Of Sentences Processed: {i + 1}/{sentences_len}")
            sys.stdout.flush()
        if i % log_num == 0:
            sys.stdout.write(f"\rNumber Of Sentences Processed: {i}/{sentences_len}")
            sys.stdout.flush()

        pos_processed_sentence = " ".join([token.pos_ for token in doc])
        tag_processed_sentence = " ".join([token.tag_ for token in doc])

        pos_sentences.append(pos_processed_sentence)
        tag_sentences.append(tag_processed_sentence)

    return [pos_sentences, tag_sentences]


#process tagging
def process(source_file_path, result_file_name, language_id, batch_size_, core_num):

    #disable unnecessary pipes
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in const.ALLOWED_PIPE_NAMES_LIKE]
    print("Disabling pipes: ", other_pipes)
    nlp.disable_pipes(*other_pipes)
    sentences = read_file(source_file_path)
    print("File's number of rows: " + str(len(sentences)))
    # device_compatible_batch_size = read_cached_batch_size()
    load_model(language_id)
    processed_sentences = pos_tag_sentences(sentences, batch_size_)
    write_pos_tagged_file(processed_sentences[0], processed_sentences[1] , result_file_name)

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