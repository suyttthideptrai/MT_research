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

SRC_COLUMN = 'Source'
TGT_COLUMN = 'Target'
CORPUS_COLUMN = 'Label'

DEFAULT_DEV_ROW = 2000
DEFAULT_TEST_ROW = 2000

main_df = pd.DataFrame(columns=[SRC_COLUMN, TGT_COLUMN, CORPUS_COLUMN])
validation_df = pd.DataFrame(columns=[SRC_COLUMN, TGT_COLUMN])
test_df = pd.DataFrame(columns=[SRC_COLUMN, TGT_COLUMN])
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


def filter_corpus_dict(file_paths):
    """ Filter corpus names for further processing """
    global corpus_dict
    cp_num = 1
    for cp_path in file_paths:
        corpus_name = get_corpus_name_by_path(cp_path)
        print(corpus_name)
        corpus_dict[cp_num] = corpus_name
        cp_num += 1
    for key, value in corpus_dict.items():
        print(f"Corpus {key}: {value}")


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
    df["Source-Copied"] = df[SRC_COLUMN] == df[TGT_COLUMN]
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
    df["Too-Long"] = ((df[SRC_COLUMN].str.count(' ') + 1) > (
            df[TGT_COLUMN].str.count(' ') + 1) * 2) | \
                     ((df[TGT_COLUMN].str.count(' ') + 1) > (
                             df[SRC_COLUMN].str.count(' ') + 1) * 2) | \
                     ((df[SRC_COLUMN].str.count(' ') + 1) > 200) | \
                     ((df[TGT_COLUMN].str.count(' ') + 1) > 200)
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


def split_data_frame(corpus_id, dev_num_p_c, test_num_p_c):
    """ Write """
    #Tính tỉ lệ dev row dựa vào số corpus và số dev_num
    #Với mỗi corpus, lọc frame với id corpus tương ứng
    #Sample với số được tính ra với mỗi corpus ID, append vào một dataframe mới
    #Sau khi loop qua tất cả corpus, shuffle dataframe dev và test, ghi file ra
    global main_df, validation_df, test_df, corpus_dict

    # Filter out data by corpus id
    df_filtered_by_c_id = (main_df[main_df[CORPUS_COLUMN] == corpus_id]
                           .sample(n=dev_num_p_c))
    # Sample dev set
    validation_df = pd.concat([validation_df, df_filtered_by_c_id], axis=0)
    main_df.drop(df_filtered_by_c_id.index, inplace=True)
    print(f"0Validation Frame rows after: {validation_df.shape[0]}, dev_df {len(df_filtered_by_c_id.index)}")
    print(f"0Total Corpus {corpus_id} reduced to: {df_filtered_by_c_id.shape[0]}")
    print(f"0Total Train rows reduced to: {main_df.shape[0]} after extract .dev")

    if test_num_p_c == 0:
        return

    df_c_id_sample_t = (main_df[main_df[CORPUS_COLUMN] == corpus_id]
                           .sample(n=test_num_p_c))
    # print(f"test r sampled: {len(df.index)}")
    test_df = pd.concat([test_df, df_c_id_sample_t], axis=0)
    main_df.drop(df_c_id_sample_t.index, inplace=True)
    print(f"1Test Frame rows after: {test_df.shape[0]}, test_df {len(df_c_id_sample_t.index)}")
    print(f"1Total Corpus {corpus_id} reduced to: {df_filtered_by_c_id.shape[0]}")
    print(f"1Total Train rows reduced to: {main_df.shape[0]} after extract .test")

    print(f"-------------------------------------------------")



def handle_write_result_files(src_lang_id, tgt_lang_id, output_file_path, dev_num, test_num):
    global main_df, validation_df, test_df, corpus_dict
    """ Write processed result files """
    #Tính tỉ lệ dev row dựa vào số corpus và số dev_num
    #Với mỗi corpus, lọc frame với id corpus tương ứng
    #Sample với số được tính ra với mỗi corpus ID, append vào một dataframe mới
    #Sau khi loop qua tất cả corpus, shuffle dataframe dev và test, ghi file ra
    print(f"Processing validation and test data (rows): {dev_num}, {test_num}")
    print(f"{src_lang_id} + {tgt_lang_id} + {output_file_path}")
    is_process_test = test_num > 0
    dev_row_foreach = math.ceil(dev_num / len(corpus_dict))
    test_row_foreach = math.ceil(test_num / len(corpus_dict)) if is_process_test else 0
    print(f"Dev rows for each corpus: {dev_row_foreach}")
    print(f"Test rows for each corpus: {test_row_foreach}")

    for key in corpus_dict:
        split_data_frame(key, dev_row_foreach, test_row_foreach)

    path_separator = os.path.sep

    main_df = main_df.sample(frac=1).reset_index(drop=True)
    validation_df = validation_df.sample(frac=1).reset_index(drop=True)

    # Get file names
    source_file_train = (output_file_path + path_separator + "processed." + src_lang_id + ".train")
    target_file_train = (output_file_path + path_separator + "processed." + tgt_lang_id + ".train")
    # Write the dataframe to two Source and Target files
    main_df[[SRC_COLUMN]].to_csv(source_file_train, header=False, index=False,
                                             quoting=csv.QUOTE_NONE, sep="\n")
    print("Train File Saved:", source_file_train)
    main_df[[TGT_COLUMN]].to_csv(target_file_train, header=False, index=False,
                                             quoting=csv.QUOTE_NONE, sep="\n")
    print("Train File Saved:", target_file_train)

    # Write validation and test files
    source_file_dev = (output_file_path + path_separator + "processed." + src_lang_id + ".dev")
    target_file_dev = (output_file_path + path_separator + "processed." + tgt_lang_id + ".dev")

    validation_df[[SRC_COLUMN]].to_csv(source_file_dev, header=False, index=False,
                                 quoting=csv.QUOTE_NONE, sep="\n")
    print("Dev File Saved:", source_file_dev)
    validation_df[[TGT_COLUMN]].to_csv(target_file_dev, header=False, index=False,
                                 quoting=csv.QUOTE_NONE, sep="\n")
    print("Dev File Saved:", target_file_dev)

    if test_num == 0:
        return

    test_df = test_df.sample(frac=1).reset_index(drop=True)

    source_file_test = (output_file_path + path_separator + "processed." + src_lang_id + ".test")
    target_file_test = (output_file_path + path_separator + "processed." + tgt_lang_id + ".test")

    test_df[[SRC_COLUMN]].to_csv(source_file_test, header=False, index=False,
                                    quoting=csv.QUOTE_NONE, sep="\n")
    print("Test File Saved:", source_file_test)
    test_df[[TGT_COLUMN]].to_csv(target_file_test, header=False, index=False,
                                    quoting=csv.QUOTE_NONE, sep="\n")
    print("Test File Saved:", target_file_test)





def process(src_id, tgt_id, dev_num, test_num, zip_paths, output_path):
    """ Process Data """
    global main_df, corpus_dict
    corpus_no = 0
    sample_corpus_paths = []
    for zip_path in zip_paths:
        corpus_no += 1
        print(f"Processing corpus no {corpus_no} : {os.path.basename(zip_path)}")
        directory_path = get_dirname_by_path(zip_path)
        unzip_corpus(zip_path, directory_path)
        src_file = get_data_filepath_by_language_id(directory_path, src_id)
        tgt_file = get_data_filepath_by_language_id(directory_path, tgt_id)
        print(f"Source file: {src_file}")
        print(f"Target file: {tgt_file}")
        filter_and_merge_data(src_file, tgt_file, corpus_no)
        sample_corpus_paths.append(src_file)
    filter_corpus_dict(sample_corpus_paths)
    print(f"Total corpus: {corpus_no}")
    print(corpus_dict)
    print(f"Rows after processed {corpus_no} corpus: {main_df.shape[0]}")
    handle_write_result_files(src_id, tgt_id, output_path, dev_num, test_num)


def filter_and_merge_data(source_file, target_file, corpus_no):
    """ Process & Merge data to main dataset """
    global main_df
    df_source = pd.read_csv(source_file, names=[SRC_COLUMN], sep="\0", quoting=csv.QUOTE_NONE, skip_blank_lines=False,
                            on_bad_lines="skip")
    df_target = pd.read_csv(target_file, names=[TGT_COLUMN], sep="\0", quoting=csv.QUOTE_NONE, skip_blank_lines=False,
                            on_bad_lines="skip")
    if len(df_source) != len(df_target):
        raise ValueError("Source and target files have different number of lines")
    #Concat two data columns
    df_corpus = pd.concat([df_source, df_target], axis=1)
    #Filter data
    df_corpus = filter_data(df_corpus, corpus_no)
    #Concat corpus label for file output handling
    df_label = pd.DataFrame({CORPUS_COLUMN: [corpus_no] * len(df_corpus)})
    df_corpus = pd.concat([df_corpus, df_label], axis=1)
    print(f"Processed corpus dataframe shape (rows, columns): {df_corpus.shape}")
    columns_to_print = [SRC_COLUMN, TGT_COLUMN]
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
    parser.add_argument('--dev', type=int, default=DEFAULT_DEV_ROW, help='Number of output .dev rows')
    parser.add_argument('--test', type=int, default=0, help='Number of output .test rows')
    parser.add_argument('--result_path', type=str, default="./", help='Result Path')
    parser.add_argument('zip_file_paths', nargs='*', help='Additional zip file paths (array input)')
    return parser.parse_args()




if __name__ == '__main__':
    args = get_arg()
    src_lang_id = args.src
    tgt_lang_id = args.tgt
    dev_row = args.dev
    test_row = args.test
    result_path = args.result_path
    zip_file_paths = args.zip_file_paths
    print(f"params  :\n"
          f"src     : {src_lang_id}\n"
          f"tgt     : {tgt_lang_id}\n"
          f"dev     : {dev_row}\n"
          f"test    : {test_row}\n"
          f"save_to : {result_path}\n"
          f"files   : {zip_file_paths}\n")
    start_time = time.time()
    process(src_lang_id, tgt_lang_id, dev_row, test_row, zip_file_paths, result_path)
    end_time = time.time()
    print(f"Done data processing in {end_time - start_time} seconds")
