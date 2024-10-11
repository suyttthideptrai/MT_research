# https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/moses/en-vi.txt.zip
#Read & Write files, get device compatible batch size
import math
import os
import time
import zipfile

def unzip_corpus(corpus_file_path, output_path):
    # Check if the zip file exists
    if not os.path.exists(corpus_file_path):
        print(f"Error: '{corpus_file_path}' does not exist.")
        return
    # Check if the extract folder exists, if not create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # Unzipping the file
    with zipfile.ZipFile(corpus_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_path)
        print(f"Unzipped '{corpus_file_path}' to '{output_path}' successfully.")



def read_corpus(corpus_file_path, src_lang_id, tgt_lang_id):
    print(f"Reading corpus from: {corpus_file_path}")
    with zipfile.ZipFile(corpus_file_path, 'r') as zip_ref:
        zip_ref.extractall('data')



