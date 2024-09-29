import os
import xml.etree.ElementTree as ET

#@author Hồng Đức
def read_corpus(file_path, lang_id):
    sentences = []
    if file_path.endswith(".xml"):
        sentences = extract_from_xml(file_path)
    elif file_path.endswith(f".{lang_id}"):
        with open(file_path, 'r', encoding='utf-8') as f:
            sentences = f.readlines()
    elif file_path.endswith(".ids"):  
        sentences = read_ids_file(file_path)
    return sentences
def extract_from_xml(file_path):
    # Hàm mẫu để lấy dữ liệu từ tệp XML
    sentences = []
    try:
        # Phân tích tệp XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        # Giả sử các câu được đặt trong thẻ <sentence>
        for sentence in root.findall(".//sentence"):
            text = sentence.text.strip()
            if text:
                sentences.append(text)
    except ET.ParseError as e:
        print(f"Lỗi khi phân tích tệp XML: {file_path} - {e}")
    return sentences
def read_ids_file(file_path):
    sentences = []
    with open(file_path, 'r', encoding='utf-8') as f:
        sentences = f.readlines()  
    return sentences
