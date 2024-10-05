import py_vncorenlp
from helpers.check_models import check_models
from helpers.reformat_wordsegment_output import reformat_wordsegment_output as wordsegment
import os

# for word segmentation 
# download wordsegment component and jar
# passing corpus into wordsegemnt mcomponent => create wordsegment file  "Tiến_Thành ơi , em yêu anh ! Xin_lỗi , anh chỉ coi em là chị !"
# return path to wordsegment file 
def vn_nlp():
    abspath = os.path.abspath("./src/pos/vn/")
    print(abspath)
    # path to VNCoreNLP and model
    file_path = "./src/pos/vn/VNCoreNLP-1.2.jar"
    dir_path = "./src/pos/vn/models"


    # path to input and output files
    input_file = abspath + "/output/output_corpus.txt"  
    output_file = abspath +'/output/pre_output.txt' 
    wordsegment_file = abspath + "/output/word_segmented.txt"

    if ( not check_models(file_path, dir_path) ) :
        py_vncorenlp.download_model(save_dir=abspath + "/vncorenlp")

    # Load VnCoreNLP from the local working folder that contains both `VnCoreNLP-1.2.jar` and `models` 
    rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir= abspath + "/vncorenlp")
    # Equivalent to: rdrsegmenter = py_vncorenlp.VnCoreNLP(, "ner", "parse"], save_dir='/absolute/path/to/vncorenlp')

    # Annotate a raw corpus
    # output/output_corpus.txt as input.txt (after reading corpus) then generate a word_segment file
    rdrsegmenter.annotate_file(input_file= input_file, output_file= output_file)

    # Reformat the content in file and generate a final file
    return wordsegment(output_file, wordsegment_file)
