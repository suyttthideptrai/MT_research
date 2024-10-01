# import spacy
# from transformers import AutoModel
#
# phobert = AutoModel.from_pretrained("vinai/phobert-base-v2")
# nlp = spacy.load(phobert)
#
# doc = nlp("Ông Nguyễn Khắc Chúc  đang làm việc tại Đại học Quốc gia Hà Nội. Bà Lan, vợ ông Chúc, cũng làm việc tại đây.")
#
# print(doc.text)
# # Print the headers
# print(f"{'Token':<15} {'POS':<10} ")
#
# # Iterate over tokens in the document
# for token in doc:
#     print(f"{token.text:<15} {token.pos_:<10}")
