import os
from dotenv import load_dotenv
import openai
import numpy as np
from tqdm import tqdm
import tiktoken

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

TEXT_DIR = "texts"
EMBEDDINGS_FILE = "embeddings_chunked.npy"
METADATA_FILE = "metadata_chunked.txt"
CHUNK_SIZE = 500  # token

def chunk_text(text, max_tokens=CHUNK_SIZE, encoding_name="cl100k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = enc.decode(tokens[i:i+max_tokens])
        chunks.append(chunk)
    return chunks

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return np.array(response.data[0].embedding)

embeddings = []
metadata = []

for fname in tqdm(os.listdir(TEXT_DIR)):
    if not fname.endswith(".txt"):
        continue
    path = os.path.join(TEXT_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = chunk_text(content)
    for idx, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        embeddings.append(emb)
        metadata.append(f"{fname}||chunk_{idx}")

np.save(EMBEDDINGS_FILE, np.array(embeddings))
with open(METADATA_FILE, "w") as f:
    for m in metadata:
        f.write(m + "\n")

print("✅ Chunk bazlı embedding işlemi tamamlandı.")