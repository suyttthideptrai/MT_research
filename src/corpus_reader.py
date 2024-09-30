import zipfile

#@ author Hồng Đức
def read_corpus_pairs(zip_path, langId_src, langId_tgt):
    src_sentences = []
    tgt_sentences = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        # Tìm tệp ngôn ngữ theo langId_src và langId_tgt
        src_file = [f for f in file_list if f.endswith(f".{langId_src}")][0]
        tgt_file = [f for f in file_list if f.endswith(f".{langId_tgt}")][0]

        # Đọc file source và target song song
        with zip_ref.open(src_file) as f_src, zip_ref.open(tgt_file) as f_tgt:
            src_lines = f_src.readlines()
            tgt_lines = f_tgt.readlines()

            # Đảm bảo số câu khớp giữa ngôn ngữ nguồn và đích
            assert len(src_lines) == len(tgt_lines), "Số câu trong file nguồn và file đích không khớp."

            # Lưu từng cặp câu vào danh sách
            src_sentences = [src_line.decode('utf-8').strip() for src_line in src_lines]
            tgt_sentences = [tgt_line.decode('utf-8').strip() for tgt_line in tgt_lines]

    return src_sentences, tgt_sentences
