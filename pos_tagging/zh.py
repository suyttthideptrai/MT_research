# POS tagging Chinese sentence for Machine Translation
# Command: python3 zh.py <source_file_zh> <result_file_name>
import spacy
import os
import sys
from file_utils import read_file, write_pos_tagged_file

SPACY_MODEL_NAME_ZH = "zh_core_web_md"
PREFERRED_EXTENSION = ".zh"
# install vocab model from spacy.io
cache_dir = os.getenv("cache_dir", "../../models")
model_path = SPACY_MODEL_NAME_ZH
# Create cache directory if it doesn't exist
os.makedirs(cache_dir, exist_ok=True)
try:
    nlp = spacy.load(os.path.join(cache_dir, model_path))
except OSError:
    print("Downloading model " + model_path + "...")
    spacy.cli.download(model_path)
    print("Loading model ...")
    nlp = spacy.load(model_path)
    nlp.to_disk(os.path.join(cache_dir, model_path))

def get_default_result_filename(file_path):
    file_name = os.path.basename(file_path)
    return file_name

def pos_tag_sentences(sentences):
    pos_sentences = []
    tag_sentences = []
    for i in range(len(sentences)):
        doc = nlp(sentences[i])
        sys.stdout.write(f"\rProcessing sentence no: {i}")
        sys.stdout.flush()
        pos_processed_sentence = ""
        tag_processed_sentence = ""
        for token in doc:
            # processed_sentence += (token.text + "/" + token.pos_ + "/" + token.tag_ + "/" + token.dep_ + " ")
            pos_processed_sentence += (token.pos_ + " ")
            tag_processed_sentence += (token.tag_ + " ")
        pos_sentences.append(pos_processed_sentence)
        tag_sentences.append(tag_processed_sentence)
    return [pos_sentences, tag_sentences]


#process tagging
def process(source_file_zh, result_file_name):
    sentences = read_file(source_file_zh)
    print("File's number of rows: " + str(len(sentences)))
    processed_sentences = pos_tag_sentences(sentences)
    write_pos_tagged_file(processed_sentences[0], processed_sentences[1] , result_file_name)

if __name__ == '__main__':
    source_file_zh = sys.argv[1]
    result_file_name = sys.argv[2] if len(sys.argv) > 2 else get_default_result_filename(source_file_zh)
    if not source_file_zh.endswith(PREFERRED_EXTENSION):
        print("Wrong file extension: " + source_file_zh + " Please try another file with đuôi " + PREFERRED_EXTENSION)
        exit(1)
    print("Processing... Source File: " + source_file_zh)
    process(source_file_zh, result_file_name)