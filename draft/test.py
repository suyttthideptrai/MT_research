import spacy
import pandas as pd

from spacy.lang.vi.examples import sentences
from pos_tagging import constants as const


def spacy_test():
    nlp = spacy.load(const.SPACY_TAGGING_MODELS["vi"])

    # nlp = spacy.load("zh_core_web_md-3.8.0-py3-none-any.whl")
    doc = nlp(sentences[0])
    print(doc.text)
    # Print the headers
    print(f"{'Token':<15} {'Lemma':<15} {'POS':<10} {'Tag':<10} {'Dep':<15} {'Shape':<10} {'Is Alpha':<10} {'Is Stop'}")

    # Iterate over tokens in the document
    for token in doc:
        print(f"{token.text:<15} {token.lemma_:<15} {token.pos_:<10} {token.tag_:<10} {token.dep_:<15} "
              f"{token.shape_:<10} {token.is_alpha:<10} {token.is_stop}")

def read_file(file_path):
    print(f"Reading file from: {file_path}")
    df = pd.read_csv(file_path, sep='\0', header=None, skip_blank_lines=False, on_bad_lines="skip")
    print("Dataframe shape (rows, columns):", df.shape)


if __name__ == '__main__':
    read_file("../test_data/test_data.en")


