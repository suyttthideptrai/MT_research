import torch
from transformers import AutoModel, AutoTokenizer
from transformers import logging
import re
logging.set_verbosity_warning()
from vn_wordsegment_script import vn_nlp

# dowload model and tokenizer
phobert = AutoModel.from_pretrained("vinai/phobert-base-v2")
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")

# INPUT TEXT MUST BE ALREADY WORD-SEGMENTED!
# Handle word-sengment taskd for Vn and return a path to wordsegment file
wordsegemnt_file = vn_nlp()

print ("Wordsegement path : ", wordsegemnt_file)

# Receive wordsegment file and downloaded tokenizer and handle each sentence (separated)
def encode_sentences_from_file(input_file_path, tokenizer):
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        content = infile.read()  # Read the entire content of the file

    # Use regex to split the content into sentences based on valid punctuation marks
    sentences = re.split(r'(?<=[.!?...;]) +', content)  # Split at sentence-ending punctuation

    for sentence in sentences:
        sentence = sentence.strip()  # Remove any surrounding whitespace or newlines
        if sentence:  # Check if the sentence is not empty
            encoded_tensor = torch.tensor([tokenizer.encode(sentence)])
            with torch.no_grad():
                features = phobert(encoded_tensor)  # Models outputs are now tuples
                print(features)
    #         encoded_sentences.append(encoded_tensor)  # Store the tensor in the list
encode_sentences_from_file(input_file_path = wordsegemnt_file, tokenizer = tokenizer)   


## With TensorFlow 2.0+:
# from transformers import TFAutoModel
# phobert = TFAutoModel.from_pretrained("vinai/phobert-base")