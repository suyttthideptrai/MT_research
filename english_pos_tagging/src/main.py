import os
from pos_tagger import pos_tag_sentences
from file_utils import read_file, write_pos_tagged_file

def main(input_file, output_file):
    # Đọc file input
    sentences = read_file(input_file)
    
    # Gán POS tags cho từng dòng
    pos_tagged_sentences = pos_tag_sentences(sentences)
    
    # Ghi kết quả ra file output
    write_pos_tagged_file(pos_tagged_sentences, output_file)

if __name__ == "__main__":
    # Đường dẫn file input và output
    input_file = r"english_pos_tagging\input\input.txt"  # Thay bằng đường dẫn file của bạn
    output_file = r"english_pos_tagging\output\output_pos_tagged.txt"  # File kết quả
    
    # Chạy chương trình
    main(input_file, output_file)
