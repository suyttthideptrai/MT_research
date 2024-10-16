# POS tagging English sentence for Machine Translation
# Command: python3 tagger.py <source_file> <lang_id> <result_file_name> <batch_size> <cpu_cores_num>
import sys
import constants as const
from utils import get_file_name_by_path, check_extension_is_one_of
from core import process


if __name__ == '__main__':
    source_file_path = sys.argv[1]
    language_id = sys.argv[2]
    result_file_name = sys.argv[3] if len(sys.argv) > 3 else get_file_name_by_path(source_file_path)
    batch_size = sys.argv[4] if(len(sys.argv) > 4) else const.DEFAULT_TAGGING_BATCH_SIZE
    number_of_cores = sys.argv[5] if(len(sys.argv) > 5) else const.DEFAULT_TAGGING_CORE_NUM
    if not check_extension_is_one_of(source_file_path, const.ALLOWED_LANGUAGE_IDS) and not language_id in const.ALLOWED_LANGUAGE_IDS:
        print("Unallowed language ID: " + source_file_path + " Please give a valid language ID: " + str(const.ALLOWED_LANGUAGE_IDS))
        exit(1)
    process(source_file_path, result_file_name, language_id, int(batch_size), int(number_of_cores))