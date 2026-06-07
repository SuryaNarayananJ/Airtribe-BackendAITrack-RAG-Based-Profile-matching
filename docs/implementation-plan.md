# Resume RAG System - Phase-Wise Implementation Plan

This document outlines the phase-wise implementation plan for the Resume RAG System based on the architecture document.

## Phase 1: Project Setup & Foundation
*   [x] **Directory Structure:** Initialize `data/resumes`, `data/input`, `data/output`, and `chroma_db`.
*   [x] **Dependencies:** Create `requirements.txt` to lock dependencies like `chromadb==1.5.9`, `sentence-transformers`, `pypdf`, and `python-docx`.
*   [x] **Base Scripts:** Set up the basic shell for `resume_rag.py` and `job_matcher.py`.

## Phase 2: Resume Ingestion System (Part A)
*   **Target File:** `resume_rag.py`
*   [x] **Document Parsing:** Implement extraction logic for `.pdf`, `.docx`, and `.txt` files.
*   [x] **Intelligent Chunking:** Write regex logic to detect logical resume sections (e.g., Summary, Experience, Skills) and split the text accordingly.
*   [x] **Metadata Extraction:** Extract basic metadata such as Candidate Name, Years of Experience, and core tech skills.
*   [x] **Embedding & Storage:** Utilize `sentence-transformers/all-MiniLM-L6-v2` to convert text chunks into vector embeddings and store them locally inside ChromaDB.

## Phase 3: Job Matching Engine (Part B)
*   **Target File:** `job_matcher.py`
*   [x] **Query Embedding:** Convert `.txt` job descriptions from `data/input/` into embeddings using the same sentence-transformers model.
*   [x] **Must-Have Filtering:** Parse the job description for hard requirements (e.g., Minimum Years of Experience) and immediately eliminate unqualified candidates.
*   [x] **Hybrid Search:** 
    *   [x] Query ChromaDB for Semantic Similarity.
    *   [x] Calculate a Keyword Match Score based on exact required skills.
    *   [x] Compute the final score (70% Semantic, 30% Keyword).
*   [x] **Match Reasoning & Output:** Generate a brief text explaining why the candidate was matched and save the top 10 candidates to a JSON file in `data/output/`.

## Phase 4: Jupyter Notebook & Evaluation
*   **Target File:** `notebook.ipynb`
*   [x] **Demonstration:** Provide step-by-step interactive cells showing resume loading, chunking, embedding, and storage.
*   [x] **Metrics:** Implement hooks to track ingestion latency and retrieval latency during the query phase.

## Phase 5: Testing & Deliverables
*   [x] **Data Generation:** Create a diverse dataset of at least 32 resumes (PDF/DOCX/TXT) and 7 job descriptions.
*   [x] **End-to-End Verification:** Run the full pipeline to ensure the vector database populates correctly and accurate JSON results are generated without errors.
*   [x] **Final Review:** Verify no virtual environments are utilized, strictly adhering to the global Python installation requirement.
