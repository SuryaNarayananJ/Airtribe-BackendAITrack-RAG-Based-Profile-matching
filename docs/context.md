# Resume RAG System - Project Context

## Project Overview

This project is a Resume Matching System built using Retrieval-Augmented Generation (RAG) concepts.

The system processes resumes, generates embeddings, stores them in a vector database, and retrieves the most relevant candidates for a given job description using semantic search and hybrid ranking techniques.

The project demonstrates:

* Document chunking
* Embedding generation
* Vector databases
* Semantic search
* Retrieval pipelines
* Candidate ranking and reasoning

---

# Assignment Requirements

## Learning Objectives

* Implement document chunking and embedding
* Build vector databases
* Create retrieval pipelines
* Understand semantic search

---

# Technology Stack

## Embedding Model

Library:

```text
sentence-transformers
```

Model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Reason:

* Free
* Runs locally
* No API key required
* Suitable for semantic search

---

## Vector Database

Database:

```text
ChromaDB
```

Reason:

* Free
* Lightweight
* Local storage
* Easy Python integration

---

## Programming Language

```text
Python 3.x
```

---

## Resume Parsing Libraries

```text
pypdf
python-docx
re
pathlib
```

---

# Project Structure

```text
project/
│
├── data/
│   │
│   ├── resumes/
│   │   ├── resume_1.pdf
│   │   ├── resume_2.pdf
│   │   └── ...
│   │
│   ├── input/
│   │   ├── python_developer.txt
│   │   ├── data_scientist.txt
│   │   ├── backend_engineer.txt
│   │   ├── devops_engineer.txt
│   │   └── java_developer.txt
│   │
│   └── output/
│
├── docs/
│   └── context.md
│
├── chroma_db/
│
├── resume_rag.py
├── job_matcher.py
├── notebook.ipynb
├── requirements.txt
└── README.md
```

---

# Dataset Requirements

Minimum:

```text
30+ resumes
5+ job descriptions
```

Recommended job descriptions:

* Python Developer
* Data Scientist
* Backend Engineer
* DevOps Engineer
* Java Developer

The vector database should be built once from the resume dataset.

Each job description will then be used as a separate query against the database.

---

# Part A - RAG System Setup

File:

```text
resume_rag.py
```

## Responsibilities

### Resume Loading

Load all resumes from:

```text
data/resumes/
```

Supported formats:

* PDF
* DOCX
* TXT

---

### Intelligent Chunking

Chunk resumes while preserving logical sections such as:

* Summary
* Education
* Experience
* Skills
* Projects
* Certifications

Do not split text randomly.

Each section should become a meaningful chunk.

---

### Embedding Generation

Generate embeddings for every chunk using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Workflow:

```text
Resume
    ↓
Chunking
    ↓
Embeddings
```

---

### Metadata Extraction

Extract:

```json
{
  "name": "",
  "skills": [],
  "experience_years": 0,
  "education": ""
}
```

Store metadata with every resume.

Purpose:

* Filtering
* Ranking
* Match reasoning

---

### Vector Storage

Store the following in ChromaDB:

* Chunk text
* Embeddings
* Resume path
* Metadata

Persist the database locally so it can be reused.

---

# Part B - Job Matching Engine

File:

```text
job_matcher.py
```

## User Workflow

### Step 1

Place resumes in:

```text
data/resumes/
```

### Step 2

Place job descriptions in:

```text
data/input/
```

### Step 3

Run:

```text
python resume_rag.py
```

This builds and stores the vector database.

### Step 4

Run:

```text
python job_matcher.py <job_description_filename.txt>
```

### Step 5

Select a job description from the available input files.

### Step 6

Results are generated and saved to:

```text
data/output/
```

---

# Semantic Search

Process:

```text
Job Description
        ↓
Generate Embedding
        ↓
Query ChromaDB
        ↓
Retrieve Top 10 Matches
```

Configuration:

```python
TOP_K = 10
```

---

# Hybrid Search

The assignment requires:

```text
Semantic Search + Keyword Search
```

### Semantic Component

Uses vector similarity between:

* Job description embeddings
* Resume embeddings

This enables matching based on meaning rather than exact wording.

---

### Keyword Component

Critical skills should also be checked.

Examples:

* Python
* Java
* AWS
* Docker
* Kubernetes
* Machine Learning
* React

Matching critical skills should increase ranking scores.

---

# Must-Have Requirement Filtering

Support mandatory requirements.

Example:

```text
Must Have:
5+ years Python experience
```

Candidate:

```text
Python experience: 2 years
```

Result:

```text
Filtered Out
```

Possible filters:

* Minimum experience
* Mandatory skills
* Certifications
* Education requirements

---

# Ranking and Scoring

Generate scores between:

```text
0 - 100
```

Suggested formula:

```text
70% Semantic Similarity
30% Keyword Match
```

Example:

```text
Semantic Score = 85
Keyword Score = 90

Final Score =
(85 × 0.7) + (90 × 0.3)
```

Scores should be normalized to a 100-point scale.

---

# Match Reasoning

Each result should include reasoning.

Example:

```text
Strong Python experience.

AWS project experience.

Machine Learning background aligns with job requirements.
```

Reasoning should be based on:

* Matched skills
* Relevant experience
* Relevant resume sections

Rule-based reasoning is sufficient.

---

# Output Format

```json
{
  "job_description": "...",
  "top_matches": [
    {
      "candidate_name": "John Doe",
      "resume_path": "data/resumes/john_doe.pdf",
      "match_score": 92,
      "matched_skills": [
        "Python",
        "Machine Learning"
      ],
      "relevant_excerpts": [
        "Developed ML models using Python..."
      ],
      "reasoning": "Strong match for ML and Python experience."
    }
  ]
}
```

---

# Output Naming Convention

Input:

```text
python_developer.txt
```

Output:

```text
python_developer_results.json
```

All output files should be stored in:

```text
data/output/
```

---

# Performance Metrics

Measure:

## Retrieval Accuracy

Examples:

```text
Top-5 Accuracy
Top-10 Accuracy
```

Measure whether relevant candidates appear in retrieved results.

---

## Latency

Measure:

* Embedding generation time
* Retrieval time
* End-to-end query time

Example:

```text
Average Query Time:
0.15 seconds
```

---

# Jupyter Notebook Requirements

Provide a notebook demonstrating:

1. Resume loading
2. Resume chunking
3. Embedding generation
4. ChromaDB storage
5. Semantic search
6. Hybrid search
7. Ranking logic
8. Accuracy evaluation
9. Latency measurements

---

# Deliverables

* resume_rag.py
* job_matcher.py
* ChromaDB database
* 30+ resumes
* 5+ job descriptions
* Jupyter notebook
* Retrieval accuracy results
* Latency measurements
* Demo video (3-4 minutes)

---

# Success Criteria

The project is complete when:

* Resumes are loaded successfully.
* Resume sections are chunked correctly.
* Embeddings are generated.
* ChromaDB is populated.
* Job descriptions retrieve relevant resumes.
* Top 10 candidates are returned.
* Match scores are generated.
* Match reasoning is generated.
* Results are saved to the output folder.
* Accuracy metrics are documented.
* Latency metrics are documented.

```
```
