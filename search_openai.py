import os
from dotenv import load_dotenv
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

TEXT_DIR = "texts"
EMBEDDINGS_FILE = "embeddings_chunked.npy"
METADATA_FILE = "metadata_chunked.txt"

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return np.array(response.data[0].embedding)

query = input("Aramak istediğiniz soruyu/metni girin: ")
query_embedding = get_embedding(query).reshape(1, -1)

embeddings = np.load(EMBEDDINGS_FILE)
with open(METADATA_FILE, "r") as f:
    metadata = [line.strip() for line in f]

similarities = cosine_similarity(query_embedding, embeddings)[0]
top_n = 5
top_indices = similarities.argsort()[-top_n:][::-1]

for i in top_indices:
    meta = metadata[i]
    fname, chunk_id = meta.split("||")
    print(f"\n📄 {fname} [{chunk_id}] (Score: {similarities[i]:.4f})\n")
    with open(os.path.join(TEXT_DIR, fname), "r", encoding="utf-8") as f:
        content = f.read()
    # Chunk'ı tekrar bul
    from tiktoken import get_encoding
    enc = get_encoding("cl100k_base")
    tokens = enc.encode(content)
    idx = int(chunk_id.replace("chunk_", ""))
    chunk_tokens = tokens[idx*500:(idx+1)*500]
    chunk_text = enc.decode(chunk_tokens)
    print(chunk_text[:500], "...")