import spacy
import os

from spacy.lang.vi.examples import sentences
import constants as const


nlp = spacy.load(const.SPACY_TAGGING_MODELS["vi"])


# nlp = spacy.load("zh_core_web_md-3.8.0-py3-none-any.whl")
doc = nlp(sentences[0])
print(doc.text)
# Print the headers
print(f"{'Token':<15} {'Lemma':<15} {'POS':<10} {'Tag':<10} {'Dep':<15} {'Shape':<10} {'Is Alpha':<10} {'Is Stop'}")

# Iterate over tokens in the document
for token in doc:
    print(f"{token.text:<15} {token.lemma_:<15} {token.pos_:<10} {token.tag_:<10} {token.dep_:<15} "
          f"{token.shape_:<10} {token.is_alpha:<10} {token.is_stop}")



# import torch
# from transformers import AutoModel, AutoTokenizer
#
# phobert = AutoModel.from_pretrained("vinai/phobert-base-v2")
# tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
#
# # INPUT TEXT MUST BE ALREADY WORD-SEGMENTED!
# sentence = 'Chúng_tôi là những nghiên_cứu_viên .'
#
# input_ids = torch.tensor([tokenizer.encode(sentence)])
#
# with torch.no_grad():
#     features = phobert(input_ids)