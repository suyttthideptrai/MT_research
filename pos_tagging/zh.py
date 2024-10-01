import spacy
import os
from spacy.lang.zh.examples import sentences

#install vocab model from spacy.io
cache_dir=os.getenv("cache_dir", "../../models")
model_path="zh_core_web_md"

# Create cache directory if it doesn't exist
os.makedirs(cache_dir, exist_ok=True)

try:
    nlp = spacy.load(os.path.join(cache_dir,model_path))
except OSError:
    spacy.cli.download(model_path)
    nlp = spacy.load(model_path)
    nlp.to_disk(os.path.join(cache_dir,model_path))

# doc = nlp(sentences[0])
doc = nlp("一个插入框不能插入另一个块,如果那个块已经以一个插入框开始或是它自己就是一个插入框。")
print(doc.text)
# Print the headers
print(f"{'Token':<15} {'Lemma':<15} {'POS':<10} {'Tag':<10} {'Dep':<15} {'Shape':<10} {'Is Alpha':<10} {'Is Stop'}")

# Iterate over tokens in the document
for token in doc:
    print(f"{token.text:<15} {token.lemma_:<15} {token.pos_:<10} {token.tag_:<10} {token.dep_:<15} "
          f"{token.shape_:<10} {token.is_alpha:<10} {token.is_stop}")

