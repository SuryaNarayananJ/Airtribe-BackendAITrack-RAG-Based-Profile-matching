# Resume RAG System - Evaluation & Metrics Strategy

This document details the evaluation framework used to measure the performance, accuracy, and efficiency of the Resume RAG System.

## 1. Retrieval Accuracy Metrics

Since the core of the system relies on vector similarity, it's critical to ensure the most relevant candidates are actually surfaced.

### Top-K Accuracy (Recall@K)
*   **Definition:** Measures whether the "perfect" candidates for a given job description appear in the top `K` retrieved results.
*   **Target Metrics:** Top-5 and Top-10 Accuracy.
*   **Methodology:**
    1.  Establish a "Golden Dataset": Manually tag 3-5 perfect candidate resumes for each of the 7 Job Descriptions.
    2.  Run the query through `job_matcher.py <filename.txt>`.
    3.  If the tagged candidate appears in the output JSON, it's a hit.
*   **Goal:** Achieve >85% Top-10 accuracy across all job profiles.

### Must-Have Filtering Precision
*   **Definition:** Measures the strictness and accuracy of the rule-based filtering (e.g., minimum years of experience).
*   **Methodology:** Analyze the Top 10 results. If any candidate in the JSON output has less experience than the Job Description strictly requires, it is counted as a False Positive.
*   **Goal:** 100% precision (0 False Positives for hard constraints).

## 2. Latency Metrics

Performance is tracked to ensure the system is viable for a local environment without GPU acceleration.

### Ingestion Latency (Bulk)
*   **Definition:** The time it takes to process, chunk, and embed a batch of resumes.
*   **Measurement:** Tracked via `time.time()` in `notebook.ipynb` around the `process_resumes()` function.
*   **Expected Baseline:** For `sentence-transformers/all-MiniLM-L6-v2` on a standard CPU, processing 32 resumes (approx. 150 chunks) should take < 10 seconds.

### Query Latency (End-to-End)
*   **Definition:** The time it takes for a user to query a Job Description and receive the final JSON results.
*   **Breakdown:**
    *   *Embedding Generation:* Time to encode the JD.
    *   *Vector Retrieval:* Time to execute `collection.query()` against ChromaDB.
    *   *Scoring & I/O:* Time to compute Hybrid scores and write the JSON file.
*   **Expected Baseline:** Total query time per Job Description should be < 0.5 seconds on a CPU.

## 3. Hybrid Search Weighting Evaluation

The system uses a `70% Semantic / 30% Keyword` formula.

### A/B Testing the Weights
To optimize the system, the `notebook.ipynb` can be used to tweak the `final_score` calculation:
1.  **100% Semantic:** Good for finding candidates with transferable skills but misses specific tech stacks.
2.  **50/50 Split:** Can over-penalize candidates who didn't list a specific keyword but have equivalent semantic experience.
3.  **70/30 (Current):** Provides the best balance—rewarding strong conceptual alignment while giving a slight edge to exact tech stack matches.

## 4. Match Reasoning Review

*   **Qualitative Metric:** The human-readability and logical soundness of the output reasoning.
*   **Evaluation:** Review the `reasoning` string in the output JSONs. It should accurately reflect the candidate's actual years of experience and correctly list the overlapping skills found between their metadata and the JD.
