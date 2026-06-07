# Resume RAG System - Edge Cases & Limitations

This document outlines potential edge cases, system limitations, and failure scenarios in the Resume RAG System, along with the strategies implemented (or recommended) to mitigate them.

## 1. Document Parsing Edge Cases

### Corrupted or Protected PDFs
*   **Scenario:** A candidate uploads a password-protected or heavily image-based PDF.
*   **Impact:** `pypdf` will fail to extract text, resulting in an empty chunk and the candidate being ignored.
*   **Mitigation:** The ingestion script includes a check for empty text extraction (`if not text.strip():`). It logs a warning and skips the file gracefully without crashing the pipeline. For OCR, tools like `pytesseract` would be needed as a future enhancement.

### Unconventional Formats & Extensions
*   **Scenario:** A candidate submits an `.rtf`, `.pages`, or `.odt` file.
*   **Impact:** The system only explicitly supports `.pdf`, `.docx`, and `.txt`.
*   **Mitigation:** Files with unsupported extensions are logged and bypassed. 

## 2. Chunking & Text Processing

### Missing Standard Headers
*   **Scenario:** A resume is structured as a continuous narrative without standard headers like "Experience", "Skills", or "Education".
*   **Impact:** The Intelligent Chunker regex will not trigger, resulting in the entire resume being parsed as a single massive "General Information" chunk.
*   **Mitigation:** While not ideal for granular retrieval, the vector database will still embed the entire block. However, the system might hit token limits on the embedding model (`all-MiniLM-L6-v2` supports up to 256/512 tokens).

### Extraneous Whitespace or Weird Characters
*   **Scenario:** Resumes generated from complex web templates might parse with huge gaps, bullet point icons (like ✅ or ❖), or misaligned columns.
*   **Impact:** Semantic embeddings might be slightly skewed by noise.
*   **Mitigation:** Basic `.strip()` and regex cleaning are applied during chunking.

## 3. Metadata Extraction Limitations

### Ambiguous Years of Experience
*   **Scenario:** A candidate writes "Worked from Jan 2018 to May 2023" instead of "5 years of experience".
*   **Impact:** The simple regex rule (`r"(\d+)\+?\s*years?\s+experience"`) will fail to capture the experience, defaulting to `0` years.
*   **Mitigation:** If the Job Description has a "Must Have: 3 years" requirement, this candidate might be unfairly filtered out. A more robust NLP/NER approach (like spaCy) is recommended for production.

### Synonym Mismatch in Skills
*   **Scenario:** Candidate lists "K8s", but the hardcoded skill list only checks for "Kubernetes".
*   **Impact:** Keyword score component (30%) drops, even if semantic search still captures the similarity.
*   **Mitigation:** The keyword list should be expanded to include common acronyms and aliases.

## 4. Retrieval & Semantic Search Edge Cases

### The "Empty" Job Description
*   **Scenario:** A recruiter uploads a job description containing only one sentence: "Looking for a coder."
*   **Impact:** The resulting embedding will be sparse in context, leading to highly variable or inaccurate nearest-neighbor matches in ChromaDB.
*   **Mitigation:** The script checks for empty strings, but a minimum character limit could be enforced on Job Descriptions.

### High ChromaDB Distance Ties
*   **Scenario:** Multiple candidates have very similar generalized resumes, resulting in near-identical L2 distances.
*   **Impact:** The ranking order for the bottom 5 of the Top 10 might be arbitrary.
*   **Mitigation:** The 30% Keyword Matching and strict Must-Have filtering act as strong tie-breakers in these scenarios.
