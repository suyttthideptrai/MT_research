# Description: script will merge data from multiple zip files into one and reduce it by percentage
# Usage: process_data.py <src_lang_id> <tgt_lang_id> <percentage> <zip_file_path_1> <zip_file_path_2> <zip_file_path_3> ...

import sys

#Read & Write files, get device compatible batch size
import math
import os
import time
import zipfile

import pandas as pd
import numpy as np
import csv

def get_dirname_by_path(file_path):
    """ Get directory out of file path """
    return os.path.dirname(file_path)

def unzip_corpus(corpus_file_path, output_path):
    # Check if the zip file exists
    if not os.path.exists(corpus_file_path):
        print(f"Error: '{corpus_file_path}' does not exist.")
        return
    # Unzipping the file
    with zipfile.ZipFile(corpus_file_path, 'r') as zip_ref:
        print(f"Unzipping '{corpus_file_path}' to '{output_path}'...")
        zip_ref.extractall(output_path)
        print(f"Unzipped '{corpus_file_path}' to '{output_path}' successfully.")

def get_data_filepath_by_language_id(directory_path, lang_id):
    """ Get data file by language id """
    for file in os.listdir(directory_path):
        if file.endswith(f".{lang_id}"):
            return directory_path + os.path.sep + file
    raise FileNotFoundError(f"Data file with language id '{lang_id}' not found in '{directory_path}', program exit.")

def filter_data(data_frame, corpus_no, src_lang_id, tgt_lang_id, result_path):
    # Delete nan
    data_frame = data_frame.dropna()
    print("--- Rows with Empty Cells Deleted\t--> Rows:", data_frame.shape[0])

    # Drop duplicates
    data_frame = data_frame.drop_duplicates()
    print("--- Duplicates Deleted\t\t\t--> Rows:", data_frame.shape[0])

    # Drop copy-source rows
    data_frame["Source-Copied"] = data_frame['Source'] == data_frame['Target']
    data_frame = data_frame.set_index(['Source-Copied'])
    try:  # To avoid (KeyError: '[True] not found in axis') if there are no source-copied cells
        data_frame = data_frame.drop([True])  # Boolean, not string, do not add quotes
    except:
        pass

    data_frame = data_frame.reset_index()
    data_frame = data_frame.drop(['Source-Copied'], axis=1)
    print("--- Source-Copied Rows Deleted\t\t--> Rows:", data_frame.shape[0])

    # Drop too-long rows (source or target)
    # Based on your language, change the values "2" and "200"
    data_frame["Too-Long"] = ((data_frame['Source'].str.count(' ') + 1) > (
            data_frame['Target'].str.count(' ') + 1) * 2) | \
                             ((data_frame['Target'].str.count(' ') + 1) > (
                                     data_frame['Source'].str.count(' ') + 1) * 2) | \
                             ((data_frame['Source'].str.count(' ') + 1) > 200) | \
                             ((data_frame['Target'].str.count(' ') + 1) > 200)
    data_frame = data_frame.set_index(['Too-Long'])
    try:  # To avoid (KeyError: '[True] not found in axis') if there are no too-long cells
        data_frame = data_frame.drop([True])  # Boolean, not string, do not add quotes
    except:
        pass

    data_frame = data_frame.reset_index()
    data_frame = data_frame.drop(['Too-Long'], axis=1)
    print("--- Too Long Source/Target Deleted\t--> Rows:", data_frame.shape[0])

    # Remove HTML and normalize
    # Use str() to avoid (TypeError: expected string or bytes-like object)
    # Note: removing tags should be before removing empty cells because some cells might have only tags and become empty.
    data_frame = data_frame.replace(r'<.*?>|&lt;.*?&gt;|&?(amp|nbsp|quot);|{}', ' ', regex=True)
    data_frame = data_frame.replace(r'  ', ' ', regex=True)  # replace double-spaces with one space
    print("--- HTML Removed\t\t\t--> Rows:", data_frame.shape[0])

    # Replace empty cells with NaN
    data_frame = data_frame.replace(r'^\s*$', np.nan, regex=True)
    # Delete nan (already there, or generated from the previous steps)
    data_frame = data_frame.dropna()
    print("--- Rows with Empty Cells Deleted\t--> Rows:", data_frame.shape[0])

    # Shuffle the data
    data_frame = data_frame.sample(frac=1).reset_index(drop=True)
    print("--- Rows Shuffled\t\t\t--> Rows:", data_frame.shape[0])

    if corpus_no < 0:
        name_sep = "_"
    else:
        name_sep = "_" + corpus_no + "_"

    path_separator = os.path.sep

    # Write the dataframe to two Source and Target files
    source_file = result_path + path_separator + "corpus" + name_sep + "filtered." + src_lang_id
    target_file = result_path + path_separator + "corpus" + name_sep + "filtered." + tgt_lang_id

    # Save source and target to two text files
    df_source = data_frame["Source"]
    df_target = data_frame["Target"]

    df_source.to_csv(source_file, header=False, index=False, quoting=csv.QUOTE_NONE, sep="\n")
    print("--- Source Saved:", source_file)
    df_target.to_csv(target_file, header=False, index=False, quoting=csv.QUOTE_NONE, sep="\n")
    print("--- Target Saved:", target_file)

def process(src_id, tgt_id, dev_perc, zip_paths, output_path, is_split=True):
    """ Process Data """
    main_df = pd.DataFrame()
    corpus_no = 1
    if is_split:
        corpus_no = -1
    for zip_path in zip_paths:
        print(f"Processing corpus no {corpus_no} : {os.path.basename(zip_path)}")
        directory_path = get_dirname_by_path(zip_path)
        unzip_corpus(zip_path, directory_path)
        src_file = get_data_filepath_by_language_id(directory_path, src_id)
        tgt_file = get_data_filepath_by_language_id(directory_path, tgt_id)
        print(f"Source file: {src_file}")
        print(f"Target file: {tgt_file}")
        merge_data(src_file, tgt_file, main_df)
        filter_data(main_df, corpus_no, src_id, tgt_id, output_path)
        corpus_no += 1


def merge_data(source_file, target_file, data_frame):
    df_source = pd.read_csv(source_file, names=['Source'], sep="\0", quoting=csv.QUOTE_NONE, skip_blank_lines=False,
                            on_bad_lines="skip")
    df_target = pd.read_csv(target_file, names=['Target'], sep="\0", quoting=csv.QUOTE_NONE, skip_blank_lines=False,
                            on_bad_lines="skip")
    if len(df_source) != len(df_target):
        raise ValueError("Source and target files have different number of lines")
    df_corpus = pd.concat([df_source, df_target], axis=1)
    print(f"Corpus dataframe shape (rows, columns): {df_corpus.shape}")
    data_frame = pd.concat([data_frame, df_corpus], axis=0)
    print(f"Main dataframe shape (rows, columns): {data_frame.shape}")


path = "../data/OpenSubtitiles/en-vi.txt.zip"
dir_path = get_dirname_by_path("../data/OpenSubtitiles/en-vi.txt.zip")
print(str(path))
process("en", "vi", 0.5, [path])





# if __name__ == '__main__':
#     src_lang_id = sys.argv[1]
#     tgt_lang_id = sys.argv[2]
#     percentage = float(sys.argv[3])
#     if percentage < 0.0 or percentage > 1.0:
#         print("Error: percentage must be between 0.0 and 1.0")
#         exit(1)
#     zip_file_paths = sys.argv[4:]
#     print(f"params: {src_lang_id}, {tgt_lang_id}, {percentage}, {zip_file_paths}")