# Legal RAG System for USCIS AAO I-140 Extraordinary Ability Decisions

## Overview
This project implements a **Retrieval Augmented Generation (RAG)** pipeline designed to help legal professionals efficiently research and answer questions about USCIS Administrative Appeals Office (AAO) non-precedent decisions, specifically focusing on I-140 Extraordinary Ability petitions published in February 2025.

The system ingests, processes, and stores legal documents, then uses OpenAI LLMs to answer complex legal queries with evidence-based, source-attributed responses.

---

## System Architecture & Design

### 1. Data Ingestion & Filtering
- **Source:** [USCIS AAO Non-Precedent Decisions](https://www.uscis.gov/administrative-appeals/aao-decisions/aao-non-precedent-decisions)
- **Filtering:**
  - Programmatically crawl the AAO decisions page.
  - Extract only documents (PDF/HTML) related to I-140 Extraordinary Ability petitions.
  - Filter by publication date (February 2025).
  - Handle both HTML and PDF links.
- **Polite Crawling:**
  - Respect `robots.txt` and website terms of use.
  - Implement rate limiting (e.g., 1 request/second) to avoid overloading the server.

### 2. Processing & Structuring
- **PDF/HTML Parsing:**
  - Convert PDFs to text using PyMuPDF.
  - Extract relevant metadata: case name, date, decision type, headings, and order/outcome.
  - Clean and structure the text for downstream processing.
- **Chunking:**
  - Split each document into ~500-token chunks using `tiktoken` to optimize retrieval granularity and LLM context usage.
  - Each chunk is associated with its source document and chunk index for traceability.

### 3. Storage
- **Vector Store:**
  - Each chunk is embedded using OpenAI's `text-embedding-3-small` model.
  - Embeddings and metadata are stored in `.npy` and `.txt` files for efficient retrieval (can be adapted to any vector DB).
  - Metadata includes file name and chunk index for source attribution.

### 4. Retrieval & Generation (RAG)
- **Query Processing:**
  - User query is embedded and compared (cosine similarity) to all chunk embeddings.
  - Top-N most relevant chunks are selected for context.
- **LLM Answering:**
  - Selected chunks are sent to OpenAI GPT-4 (or GPT-3.5-turbo) with a prompt instructing the model to answer **only using the provided context**.
  - The prompt enforces source referencing (e.g., [1], [2]) in the answer.
  - The system prints both the answer and the referenced chunks for transparency.

### 5. Evidence-Based, Source-Attributed Answers
- The LLM is prompted to cite sources for each claim, referencing the chunk numbers.
- Users can see exactly which document and chunk each part of the answer is based on.

---

## Example Workflow
1. **Ingest & Process:**
   - Download and parse all relevant AAO decisions (PDFs) for I-140 Extraordinary Ability, Feb 2025.
   - Extract text, metadata, and split into chunks.
   - Compute and store embeddings.
2. **Query:**
   - User asks: "What characteristics of national or international awards persuade the AAO that they constitute sustained acclaim?"
   - System retrieves the most relevant chunks.
   - LLM generates an answer, citing sources (e.g., "The AAO looks for evidence of major international recognition [2].").
   - Referenced chunks are displayed for verification.

---

## Reflection & Further Improvements
- **With two extra weeks:**
  - Integrate a production-grade vector database (e.g., Pinecone, ChromaDB) for scalable retrieval.
  - Build a web UI for interactive legal research.
  - Add advanced metadata extraction (e.g., named entity recognition, section labeling).
  - Implement more granular citation (e.g., sentence-level references).
  - Automate periodic data refresh from the USCIS site.

---

## Deliverables
- **Codebase:** End-to-end pipeline for legal RAG on AAO I-140 decisions.
- **README:** This document, explaining design and usage.
- **(Optional) Architecture Diagram:** See `/docs/` or attached file for a visual overview.
- **Reflection Memo:** See above.

---

## Usage
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set your OpenAI API key:**
   - Add `OPENAI_API_KEY=sk-...` to a `.env` file in the project root.
3. **Run the pipeline:**
   - Use the provided scripts to process, embed, and query the data.
   - See script comments for details.

---

## Contact
For questions or collaboration, please open an issue or contact the repo owner. 