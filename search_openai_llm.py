import os
from dotenv import load_dotenv
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken

# .env dosyasını yükle
load_dotenv()

TEXT_DIR = "texts"
EMBEDDINGS_FILE = "embeddings_chunked.npy"
METADATA_FILE = "metadata_chunked.txt"
CHUNK_SIZE = 500  # token

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return np.array(response.data[0].embedding)

def get_chunk_from_file(fname, chunk_idx, chunk_size=CHUNK_SIZE, encoding_name="cl100k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    with open(os.path.join(TEXT_DIR, fname), "r", encoding="utf-8") as f:
        content = f.read()
    tokens = enc.encode(content)
    chunk_tokens = tokens[chunk_idx*chunk_size:(chunk_idx+1)*chunk_size]
    return enc.decode(chunk_tokens)

def ask_llm_with_sources(question, docs, source_names):
    context = "\n\n".join([f"[{i+1}] {source}" for i, source in enumerate(docs)])
    prompt = f"""
You are a legal assistant. Use the following context to answer the question below. ONLY use the content provided. Reference the source number (e.g. [1], [2]) in your answer to support each claim.

Context:
{context}

Question: {question}

Answer with sources:
"""
    response = openai.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

query = input("Enter the query you want to search: ")
query_embedding = get_embedding(query).reshape(1, -1)

embeddings = np.load(EMBEDDINGS_FILE)
with open(METADATA_FILE, "r") as f:
    metadata = [line.strip() for line in f]

similarities = cosine_similarity(query_embedding, embeddings)[0]
top_n = 5
top_indices = similarities.argsort()[-top_n:][::-1]

top_chunks = []
top_sources = []
for i in top_indices:
    meta = metadata[i]
    fname, chunk_id = meta.split("||")
    chunk_idx = int(chunk_id.replace("chunk_", ""))
    chunk_text = get_chunk_from_file(fname, chunk_idx)
    top_chunks.append(chunk_text)
    top_sources.append(f"{fname} [{chunk_id}]")

answer = ask_llm_with_sources(query, top_chunks, top_sources)
print("\n🧠 LLM Response:\n", answer)

for idx, (chunk, source) in enumerate(zip(top_chunks, top_sources), 1):
    print(f"\n[{idx}] {source}\n{'-'*40}\n{chunk[:500]}\n...")
