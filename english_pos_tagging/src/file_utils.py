def read_file(file_path):
    """
    Đọc file và trả về danh sách các dòng văn bản.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def write_pos_tagged_file(pos_tagged_sentences, output_file):
    """
    Ghi kết quả POS tagged vào file đầu ra.
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        for sentence in pos_tagged_sentences:
            # Mỗi từ kèm với POS tag, nối bằng dấu /
            tagged_sentence = ' '.join([f"{word}/{tag}" for word, tag in sentence])
            file.write(tagged_sentence + '\n')
def read_file(file_path):
    print(f"Reading file from: {file_path}")  # Thêm dòng này để in ra đường dẫn file
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()
