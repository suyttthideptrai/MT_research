# Description: script will merge data from multiple zip files into one and reduce it by percentage
# Usage: process_data.py <src_lang_id> <tgt_lang_id> <percentage> <zip_file_path_1> <zip_file_path_2> <zip_file_path_3> ...

import sys

#Read & Write files, get device compatible batch size
import math
import os
import time
import zipfile
import argparse

import pandas as pd
import numpy as np
import csv
import constants as const

COL_SRC = const.SRC_COLUMN_NAME
COL_TGT = const.TGT_COLUMN_NAME

# Process Variables
DEV_ROWS = const.DEFAULT_DEV_ROW
TEST_ROWS = const.DEFAULT_TEST_ROW
RESULT_PATH = "./data"
SRC_LANG_ID = ""
TGT_LANG_ID = ""
ZIP_FILE_PATHS = []


# init dataframes
main_df = pd.DataFrame(columns=[COL_SRC, COL_TGT])
validation_df = pd.DataFrame(columns=[COL_SRC, COL_TGT])
test_df = pd.DataFrame(columns=[COL_SRC, COL_TGT])
corpus_dict = {}


def get_dirname_by_path(file_path):
    """ Get directory out of file path """
    return os.path.dirname(file_path)


def get_corpus_name_by_path(file_path):
    """ Get corpus name """
    f_name = os.path.splitext(os.path.basename(file_path))[0]
    return os.path.splitext(f_name)[0]


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


def filter_data(df, corpus_no):
    """ Filter training data in data frame """
    # Delete nan
    print(f"Filtering data for corpus no: {corpus_no}")
    df = df.dropna()
    print("--- Rows with Empty Cells Deleted\t--> Rows:", df.shape[0])
    # Drop duplicates
    df = df.drop_duplicates()
    print("--- Duplicates Deleted\t\t\t--> Rows:", df.shape[0])
    # Drop copy-source rows
    df["Source-Copied"] = df[COL_SRC] == df[COL_TGT]
    df = df.set_index(['Source-Copied'])
    try:  # To avoid (KeyError: '[True] not found in axis') if there are no source-copied cells
        df = df.drop([True])  # Boolean, not string, do not add quotes
    except:
        pass
    df = df.reset_index()
    df = df.drop(['Source-Copied'], axis=1)
    print("--- Source-Copied Rows Deleted\t\t--> Rows:", df.shape[0])
    # Drop too-long rows (source or target)
    # Based on your language, change the values "2" and "200"
    df["Too-Long"] = ((df[COL_SRC].str.count(' ') + 1) > (
            df[COL_TGT].str.count(' ') + 1) * 2) | \
                     ((df[COL_TGT].str.count(' ') + 1) > (
                             df[COL_SRC].str.count(' ') + 1) * 2) | \
                     ((df[COL_SRC].str.count(' ') + 1) > 200) | \
                     ((df[COL_TGT].str.count(' ') + 1) > 200)
    df = df.set_index(['Too-Long'])
    try:  # To avoid (KeyError: '[True] not found in axis') if there are no too-long cells
        df = df.drop([True])  # Boolean, not string, do not add quotes
    except:
        pass
    df = df.reset_index()
    df = df.drop(['Too-Long'], axis=1)
    print("--- Too Long Source/Target Deleted\t--> Rows:", df.shape[0])
    # Remove HTML and normalize
    # Use str() to avoid (TypeError: expected string or bytes-like object)
    # Note: removing tags should be before removing empty cells because some cells might have only tags and become empty.
    df = df.replace(r'<.*?>|&lt;.*?&gt;|&?(amp|nbsp|quot);|{}', ' ', regex=True)
    df = df.replace(r'  ', ' ', regex=True)  # replace double-spaces with one space
    print("--- HTML Removed\t\t\t--> Rows:", df.shape[0])
    # Replace empty cells with NaN
    df = df.replace(r'^\s*$', np.nan, regex=True)
    # Delete nan (already there, or generated from the previous steps)
    df = df.dropna()
    print("--- Rows with Empty Cells Deleted\t--> Rows:", df.shape[0])
    df = df.reset_index(drop=True)
    #
    # # Shuffle the data
    # df = df.sample(frac=1).reset_index(drop=True)
    # print("--- Rows Shuffled\t\t\t--> Rows:", df.shape[0])
    return df


def split_and_drop_dev(filtered_df):
    """ Handle split dev, drop index then return df """
    global validation_df
    dev_row_foreach = math.ceil(DEV_ROWS / len(ZIP_FILE_PATHS))
    val_sample_df = filtered_df.sample(n = dev_row_foreach)
    try:
        filtered_df = filtered_df.drop(val_sample_df.index)
    except:
        pass
    validation_df = pd.concat([validation_df, val_sample_df], axis=0)
    print(f"Sampled {val_sample_df.shape[0]} rows for validation, val frame after: {validation_df.shape[0]}")
    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df


def split_and_drop_test(filtered_df):
    """ Handle split test, drop index then return df """
    global test_df, TEST_ROWS, ZIP_FILE_PATHS
    # filtered_df = filtered_df.reset_index(drop=True)
    test_row_foreach = math.ceil(TEST_ROWS / len(ZIP_FILE_PATHS))
    test_sample_df = filtered_df.sample(n = test_row_foreach)
    try:
        filtered_df = filtered_df.drop(index=validation_df.index)
    except:
        pass
    test_df = pd.concat([test_df, test_sample_df], axis=0)
    print(f"Sampled {test_sample_df.shape[0]} rows for validation, val frame after: {test_df.shape[0]}")
    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df


def handle_write_result_files():
    """ Write processed result files """
    global main_df, validation_df, test_df, corpus_dict, SRC_LANG_ID, TGT_LANG_ID, DEV_ROWS, TEST_ROWS, RESULT_PATH

    print(f"Processing validation and test data (rows): {DEV_ROWS}, {TEST_ROWS}")

    path_separator = os.path.sep

    main_df = main_df.sample(frac=1).reset_index(drop=True)
    validation_df = validation_df.sample(frac=1).reset_index(drop=True)

    # Get file names
    source_file_train = (RESULT_PATH + path_separator + "processed." + SRC_LANG_ID + ".train")
    target_file_train = (RESULT_PATH + path_separator + "processed." + TGT_LANG_ID + ".train")
    # Write the dataframe to two Source and Target files
    main_df[[COL_SRC]].to_csv(source_file_train, header=False, index=False,
                              quoting=csv.QUOTE_NONE, sep="\n")
    print("Train File Saved:", source_file_train)
    main_df[[COL_TGT]].to_csv(target_file_train, header=False, index=False,
                              quoting=csv.QUOTE_NONE, sep="\n")
    print("Train File Saved:", target_file_train)

    if DEV_ROWS == 0:
        return

    # Write validation and test files
    source_file_dev = (RESULT_PATH + path_separator + "processed." + SRC_LANG_ID + ".dev")
    target_file_dev = (RESULT_PATH + path_separator + "processed." + TGT_LANG_ID + ".dev")

    validation_df[[COL_SRC]].to_csv(source_file_dev, header=False, index=False,
                                    quoting=csv.QUOTE_NONE, sep="\n")
    print("Dev File Saved:", source_file_dev)
    validation_df[[COL_TGT]].to_csv(target_file_dev, header=False, index=False,
                                    quoting=csv.QUOTE_NONE, sep="\n")
    print("Dev File Saved:", target_file_dev)

    if TEST_ROWS == 0:
        return

    test_df = test_df.sample(frac=1).reset_index(drop=True)

    source_file_test = (RESULT_PATH + path_separator + "processed." + SRC_LANG_ID + ".test")
    target_file_test = (RESULT_PATH + path_separator + "processed." + TGT_LANG_ID + ".test")

    test_df[[COL_SRC]].to_csv(source_file_test, header=False, index=False,
                              quoting=csv.QUOTE_NONE, sep="\n")
    print("Test File Saved:", source_file_test)
    test_df[[COL_TGT]].to_csv(target_file_test, header=False, index=False,
                              quoting=csv.QUOTE_NONE, sep="\n")
    print("Test File Saved:", target_file_test)


def process():
    """ MAIN PROCESS WORKFLOW """
    global main_df, corpus_dict, SRC_LANG_ID, TGT_LANG_ID, DEV_ROWS, TEST_ROWS, RESULT_PATH, ZIP_FILE_PATHS
    corpus_no = 0

    for zip_path in ZIP_FILE_PATHS:
        corpus_no += 1
        print(f"Processing corpus no {corpus_no} : {os.path.basename(zip_path)}")
        directory_path = get_dirname_by_path(zip_path)
        unzip_corpus(zip_path, directory_path)
        src_file = get_data_filepath_by_language_id(directory_path, SRC_LANG_ID)
        tgt_file = get_data_filepath_by_language_id(directory_path, TGT_LANG_ID)
        corpus_dict[corpus_no] = get_corpus_name_by_path(src_file)
        print(f"Source file: {src_file}")
        print(f"Target file: {tgt_file}")
        filter_split_merge_data(src_file, tgt_file, corpus_no)

    print(f"Total corpus: {corpus_no}")
    print(corpus_dict)
    print(f"Rows after processed {corpus_no} corpus: {main_df.shape[0]}")
    print(f"Validation rows sampled: {validation_df.shape[0]}")
    print(f"Test rows sampled: {test_df.shape[0]}")
    handle_write_result_files()


def filter_split_merge_data(source_file, target_file, corpus_no):
    """ Process & Split & Merge data to main dataset """
    global main_df, DEV_ROWS, TEST_ROWS
    df_source = pd.read_csv(source_file, names=[COL_SRC], sep="\0", quoting=csv.QUOTE_NONE, skip_blank_lines=False,
                            on_bad_lines="skip")
    df_target = pd.read_csv(target_file, names=[COL_TGT], sep="\0", quoting=csv.QUOTE_NONE, skip_blank_lines=False,
                            on_bad_lines="skip")
    if len(df_source) != len(df_target):
        raise ValueError("Source and target files have different number of lines")
    #Concat two data columns
    df_corpus = pd.concat([df_source, df_target], axis=1)
    #Filter data
    df_corpus = filter_data(df_corpus, corpus_no)
    #Split data
    if DEV_ROWS > 0:
        df_corpus = split_and_drop_dev(df_corpus)
    print(f"Sampled dev sentences: \n{validation_df.head(5)}\n{validation_df.tail(5)}")

    if TEST_ROWS > 0:
        df_corpus = split_and_drop_test(df_corpus)
    print(f"Sampled test sentences: \n{test_df.head(5)}\n{test_df.tail(5)}")


    #Concat corpus label for file output handling
    print(f"Processed corpus dataframe shape (rows, columns): {df_corpus.shape}")
    columns_to_print = [COL_SRC, COL_TGT]
    print(f"5 rows from head of corpus {corpus_no}: ")
    print(df_corpus[columns_to_print].head(5))
    print(f"5 rows from tail of corpus {corpus_no}: ")
    print(df_corpus[columns_to_print].tail(5))
    main_df = pd.concat([main_df, df_corpus], axis=0)
    print(f"Total rows after merging corpus {corpus_no}: {main_df.shape[0]}")


def validate_and_create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# path = "../data/QED/en-vi.txt.zip"
# path1 = "../data/Wikimedia/en-vi.txt.zip"
# dir_path = get_dirname_by_path("../data/QED/en-vi.txt.zip")
# print(str(path))
# result_path = "../data/filtered/"
# validate_and_create_dir(result_path)
# process("en", "vi", 0.5, [path, path1], result_path)

# cp_name = get_corpus_name_by_path("../data/QED/QED.en-vi.en")
# print(cp_name)

def get_arg():
    parser = argparse.ArgumentParser(description='Process Arguments')
    parser.add_argument('--src', type=str, help='Source lang ID')
    parser.add_argument('--tgt', type=str, help='Target lang ID')
    parser.add_argument('--dev', type=int, default=const.DEFAULT_DEV_ROW, help='Number of output .dev rows')
    parser.add_argument('--test', type=int, default=0, help='Number of output .test rows')
    parser.add_argument('--tag', type=bool, default=False, help='Tagging') #separate module, unusable
    parser.add_argument('--result_path', type=str, default="./data", help='Files Result Path')
    parser.add_argument('zip_file_paths', nargs='*', help='Additional zip file paths (array input)')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_arg()
    SRC_LANG_ID = args.src
    TGT_LANG_ID = args.tgt
    DEV_ROWS = args.dev
    TEST_ROWS = args.test
    RESULT_PATH = args.result_path
    ZIP_FILE_PATHS = args.zip_file_paths
    print(f"params  :                             \n"
          f"--------------------------------------\n"
          f"src     : {SRC_LANG_ID}               \n"
          f"tgt     : {TGT_LANG_ID}               \n"
          f"dev     : {DEV_ROWS}                  \n"
          f"test    : {TEST_ROWS}                 \n"
          f"save_to : {RESULT_PATH}               \n"
          f"files   :                              ")
    i = 0
    for path in ZIP_FILE_PATHS:
        i += 1
        print(f" {i}      : {path}")
    print(f"--------------------------------------\n")
    start_time = time.time()
    process()
    end_time = time.time()
    print(f"Done data processing in {end_time - start_time} seconds")
