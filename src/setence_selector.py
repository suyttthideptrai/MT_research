import random

def select_sentences(corpus_sentences, n):
    random.shuffle(corpus_sentences)  # Trộn ngẫu nhiên các câu
    return corpus_sentences[:n]  # Chọn n câu đầu tiên sau khi trộn
