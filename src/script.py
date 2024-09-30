import os
import random
import zipfile
from corpus_reader import read_corpus_pairs

# @author Hồng Đức
def get_corpus_size(zip_path):
    """Tính kích thước của corpus bằng cách lấy tổng số byte."""
    return os.path.getsize(zip_path)

def extract_sentences(corpus_paths, n, langId_src, langId_tgt):
    src_all = []
    tgt_all = []

    # Tính kích thước của từng corpus
    corpus_sizes = [get_corpus_size(path) for path in corpus_paths]
    total_size = sum(corpus_sizes)

    # Tính số lượng câu cần lấy từ mỗi corpus theo tỉ lệ kích thước
    sentence_counts = [int((size / total_size) * n) for size in corpus_sizes]

    # Đảm bảo tổng số câu không vượt quá n
    sentence_counts[-1] += n - sum(sentence_counts)

    for i, corpus_path in enumerate(corpus_paths):
        src_sentences, tgt_sentences = read_corpus_pairs(corpus_path, langId_src, langId_tgt)
        total_sentences = len(src_sentences)
        
        # Lấy số lượng câu từ corpus này theo tỉ lệ đã tính
        num_sentences_to_extract = sentence_counts[i]
        
        # Nếu số lượng câu yêu cầu lớn hơn số câu có sẵn, chỉ lấy hết các câu có sẵn
        if num_sentences_to_extract > total_sentences:
            num_sentences_to_extract = total_sentences
        
        # Chọn ngẫu nhiên số câu từ corpus này
        selected_indices = random.sample(range(total_sentences), num_sentences_to_extract)
        src_all.extend([src_sentences[i] for i in selected_indices])
        tgt_all.extend([tgt_sentences[i] for i in selected_indices])

    return src_all, tgt_all

def main(n, langId_src, langId_tgt):
    corpus_files = [
        r"data/corpus_1.zip",      # Các tệp ZIP của bạn
        r"data/corpus_2.zip",
        r"data/corpus_3.zip"
    ]

    # Trích xuất n câu từ các corpus theo tỉ lệ kích thước
    src_sentences, tgt_sentences = extract_sentences(corpus_files, n, langId_src, langId_tgt)

    # Tạo thư mục output
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Ghi các câu đã chọn ra file với định dạng source và target
    with open(f"{output_dir}/output_src.txt", 'w', encoding='utf-8') as f_src, \
         open(f"{output_dir}/output_target.txt", 'w', encoding='utf-8') as f_tgt:
        for src, tgt in zip(src_sentences, tgt_sentences):
            f_src.write(src + '\n')
            f_tgt.write(tgt + '\n')

    print(f"Đã ghi {len(src_sentences)} câu từ 3 corpus vào output_src.txt và output_target.txt")

if __name__ == "__main__":
    # Ví dụ lấy 1000 câu từ các corpus, nguồn là tiếng Việt, đích là tiếng Anh
    main(n=1000, langId_src='vi', langId_tgt='en')
