import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('punkt_tab')


def pos_tag_sentences(sentences):
    """
    Hàm này nhận vào danh sách các câu, gán POS tags cho từng câu,
    và trả về danh sách các câu với POS tags.
    """
    pos_tagged_sentences = []
    for sentence in sentences:
        # Tách từ và gán POS tag
        from nltk.tokenize import sent_tokenize, word_tokenize
        tokens = word_tokenize(sentence)
        pos_tags = nltk.pos_tag(tokens)
        pos_tagged_sentences.append(pos_tags)
    return pos_tagged_sentences
