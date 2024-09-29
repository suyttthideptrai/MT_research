import os
import xml.etree.ElementTree as ET
from corpus_reader import read_corpus
from setence_selector import select_sentences

def main(n, lang_id):
    corpus_files = [
        "data/wikimedia.en-vi.en",
        "data/wikimedia.en-vi.vi",
        "data/wikimedia.en-vi.xml",
        "data/QED.en-vi.xml",
        "data/QED.en-vi.vi",
        "data/QED.en-vi.en",
        "data/OpenSubtitles.en-vi.vi",
        "data/OpenSubtitles.en-vi.en",
        "data/OpenSubtitles.en-vi.ids"
    ]
    #Đọc corpus
    corpora = [read_corpus(file, lang_id) for file in corpus_files]
    
    #Lấy kích thước của mỗi corpus tính bằng số câu
    corpus_sizes = [len(corpus) for corpus in corpora]
    total_size = sum(corpus_sizes)

    #Tính toán số câu cần lấy từ mỗi corpus theo tỷ lệ
    num_sentences_from_each = [int(n * (size / total_size)) for size in corpus_sizes]

    #Lấy ngẫu nhiên các câu từ mỗi corpus
    selected_sentences = []
    for i, corpus in enumerate(corpora):
        selected_sentences.extend(select_sentences(corpus, num_sentences_from_each[i]))

    #Ghi các câu đã chọn vào tệp đầu ra
    with open('output/output_corpus.txt', 'w', encoding='utf-8') as f:
        for sentence in selected_sentences:
            f.write(sentence)

if __name__ == '__main__':
    #Ví dụ:
    main(n=1000, lang_id='vi')
