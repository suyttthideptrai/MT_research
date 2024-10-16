#Read & Write files, get device compatible batch size
import math
import os
import time
import constants as const

import psutil
import spacy
from spacy.lang.en.examples import sentences

cache_dir = const.MODEL_CACHE_DIR
model_path = str(const.SPACY_MODEL_NAME_EN)


def write_pos_tagged_file(tag_sentences, output_file_path):
    # Get the directory from the file path
    directory = os.path.dirname(output_file_path)

    # Check if the directory exists, and create it if it doesn't
    if not os.path.exists(directory) and directory not in ["", "."]:
        os.makedirs(directory)

    # file_name = output_file_path + const.POS_OUTPUT_POSTFIX
    # print("\nWriting pos data to file: {}".format(file_name))
    # with open(file_name, 'w', encoding='utf-8') as file:
    #     for sentence in pos_sentences:
    #         file.write(sentence + '\n')
    file_name = output_file_path + const.TAG_OUTPUT_POSTFIX
    print("\nWriting tag data to file: {}".format(file_name))
    with open(file_name, 'w', encoding='utf-8') as file:
        for sentence in tag_sentences:
            file.write(sentence + '\n')

def read_file(file_path):
    print(f"Reading file from: {file_path}")  # Thêm dòng này để in ra đường dẫn file
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()


def get_available_memory():
    """Returns the available RAM in MB."""
    mem = psutil.virtual_memory()
    return mem.available / (1024 * 1024)  # Convert bytes to MB

def read_cached_batch_size():
    """Reads the cached batch size from an environment variable."""
    cached_batch_size = os.getenv(const.CACHE_ENV_VAR)
    if cached_batch_size:
        print(f"Cached batch size found in environment: {cached_batch_size}")
        return int(cached_batch_size)
    else:
        try:
            nlp = spacy.load(os.path.join(cache_dir, model_path))
        except OSError:
            spacy.cli.download(model_path)
            nlp = spacy.load(model_path)
        batch_size = get_benchmark_batch_size(sentences, nlp)
        write_cached_batch_size(batch_size)
        return int(math.floor(batch_size))

def write_cached_batch_size(batch_size):
    """Writes the batch size to an environment variable."""
    os.environ[const.CACHE_ENV_VAR] = str(batch_size)
    print(f"Cached batch size: {batch_size} saved in environment as {const.CACHE_ENV_VAR}")


def get_benchmark_batch_size(sample_sentences, sample_nlp):
    """Finds the optimal batch size based on available memory or retrieves from cache."""

    # Check for cached batch size in environment variables
    cached_batch_size = read_cached_batch_size()
    if cached_batch_size:
        return cached_batch_size

    # Proceed to benchmark if no cache is found
    available_memory = get_available_memory()
    print(f"Available Memory: {available_memory:.2f} MB")
    max_memory = available_memory * const.MAX_MEMORY_USAGE_RATIO
    batch_size = const.INITIAL_TAGGING_BATCH_SIZE

    while True:
        print(f"\nTesting batch size: {batch_size}")
        start_time = time.time()
        try:
            # Test batch size with processing
            for _ in sample_nlp.pipe(sample_sentences[:batch_size], batch_size=batch_size):
                pass
            elapsed_time = time.time() - start_time
            memory_after = get_available_memory()
            memory_used = available_memory - memory_after

            print(f"Batch size: {batch_size}, Memory used: {memory_used:.2f} MB, Time: {elapsed_time:.2f} s")
            if memory_used > max_memory:
                print(f"Memory usage exceeded limit ({max_memory:.2f} MB). Reducing batch size.")
                break
            batch_size *= 2  # Double the batch size for the next run
        except MemoryError:
            print(f"Out of memory error at batch size {batch_size}. Reducing batch size.")
            break

    optimal_batch_size = batch_size // 2  # Return the last successful batch size
    # Cache the optimal batch size in environment variable
    write_cached_batch_size(optimal_batch_size)
    return optimal_batch_size


def get_file_name_by_path(file_path):
    """Returns the default result file name based on the source file name."""
    file_name = os.path.basename(file_path)
    return file_name


def check_extension_is_one_of(file_path, allowed_extensions):
    """Checks if the file extension is one of the allowed extensions."""
    # Get the file extension
    _, file_extension = os.path.splitext(file_path)
    # Remove the leading dot (.) from the extension and check if it's allowed
    file_extension = file_extension[1:]  # Remove the dot

    if file_extension in allowed_extensions:
        return True
    else:
        return False

