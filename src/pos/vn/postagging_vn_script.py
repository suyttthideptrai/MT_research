import py_vncorenlp
from helpers.check_models import check_models
from helpers.handle_postag import process_postag as process_word_postag
import os

abspath = os.path.abspath("./src/pos/vn/")
print(abspath)
# Example usage
file_path = "./src/pos/vn/VNCoreNLP-1.2.jar"
dir_path = "./src/pos/vn/models"


# Example usage
input_file = "./src/pos/vn/output/output_corpus.txt"  
output_file = './src/pos/vn/output/pre_output.txt' 
postag_output_file = './src/pos/vn/output/final_output.txt'

if ( not check_models(file_path, dir_path) ) :
    py_vncorenlp.download_model(save_dir=abspath)

# Load VnCoreNLP from the local working folder that contains both `VnCoreNLP-1.2.jar` and `models` 
model = py_vncorenlp.VnCoreNLP(annotators=["wseg", "pos"], save_dir= abspath)
# Equivalent to: model = py_vncorenlp.VnCoreNLP(, "ner", "parse"], save_dir='/absolute/path/to/vncorenlp')

# Annotate a raw corpus
# output/output_corpus.txt as input.txt (after reading corpus)
model.annotate_file(input_file= input_file, output_file= output_file)

process_word_postag(output_file, postag_output_file)
#final output sample: 
# word1 word2 word3
# postag1 postag2 postag3
