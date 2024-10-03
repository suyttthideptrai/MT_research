# def read_file(file_path):
#     """
#     Đọc file và trả về danh sách các dòng văn bản.
#     """
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return file.readlines()
POS_POSTFIX = ".pos"
TAG_POSTFIX = ".tag"


def write_pos_tagged_file(pos_sentences, tag_sentences, output_file):
    file_name = output_file + POS_POSTFIX
    print("\nWriting pos data to file: {}".format(file_name))
    with open(file_name, 'w', encoding='utf-8') as file:
        for sentence in pos_sentences:
            file.write(sentence + '\n')
    file_name = output_file + TAG_POSTFIX
    print("\nWriting tag data to file: {}".format(file_name))
    with open(file_name, 'w', encoding='utf-8') as file:
        for sentence in tag_sentences:
            file.write(sentence + '\n')

def read_file(file_path):
    print(f"Reading file from: {file_path}")  # Thêm dòng này để in ra đường dẫn file
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()
