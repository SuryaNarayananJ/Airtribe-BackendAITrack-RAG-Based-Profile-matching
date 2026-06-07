# AI-Powered Resume Retrieval-Augmented Generation (RAG) System

This project is an advanced, fully functional Retrieval-Augmented Generation (RAG) system designed to automate resume screening and candidate matching. It leverages **ChromaDB** for local vector storage, **HuggingFace** (`all-MiniLM-L6-v2`) for semantic embeddings, and a custom **Hybrid Search Engine** to score and rank candidates against Job Descriptions.

---

## 🛠️ Prerequisites & Installation

**Important Note:** Per project constraints, this system does *not* utilize a virtual environment. All dependencies should be installed against the global Python installation.

1. **Python 3.10+**: Ensure Python is installed on your system.
2. **Install Dependencies**: Open your terminal in the root project folder and run:
   ```bash
   pip install -r requirements.txt
   ```

*(Note: The first time you run the scripts, the `sentence-transformers` library will automatically download the AI model from the HuggingFace Hub. This may trigger a harmless warning about unauthenticated requests, which can be safely ignored).*

---

## 📁 Directory Structure

Before running the project, it's important to understand where data belongs:

*   **`data/resumes/`**: Place all candidate resumes here. Supported formats are `.pdf`, `.docx`, and `.txt`.
*   **`data/input/`**: Place your Job Description (JD) text files here (e.g., `job_description_001.txt`).
*   **`data/output/`**: The engine will save the final Top-10 matched JSON outputs here.
*   **`chroma_db/`**: The auto-generated persistent vector database directory.
*   **`docs/`**: Comprehensive project documentation including Architecture, Edge Cases, and Evaluation methodology.

---

## 🧠 How It Works Under the Hood

To understand why this system is so effective, here is a breakdown of the core AI processes happening behind the scenes:

### 1. Intelligent Chunking
A resume contains a lot of text, and if we feed the entire document to the AI at once, it loses focus. Our `resume_rag.py` script parses the resume and **chunks** (splits) it into smaller, logical blocks based on standard resume sections (e.g., Summary, Experience, Education, Skills). This ensures the AI retains the context of each specific bullet point without getting overwhelmed.

### 2. Embeddings (`all-MiniLM-L6-v2`)
Once the resumes are chunked, we convert that human-readable text into an **Embedding**. An embedding is simply a massive mathematical array (a 384-dimensional vector) that represents the *meaning* of the text. We use the open-source `sentence-transformers/all-MiniLM-L6-v2` model to generate these embeddings. For example, the model knows that the words "React" and "Frontend" are mathematically related, even if they aren't spelled the same way. 

### 3. ChromaDB (Vector Database)
Standard databases look for exact keyword matches. **ChromaDB** is a specialized Vector Database designed to store the mathematical embeddings we generated. When the user provides a Job Description, we convert that JD into an embedding as well. ChromaDB then rapidly calculates the "distance" between the JD's embedding and all the resume chunks in milliseconds. The closer the distance, the more relevant the resume chunk is to the job description!

---

## 🚀 How to Run the Project

Testing the project is a simple, two-step process:

### Step 1: Ingest the Resumes
Whenever you add new resumes to the `data/resumes/` folder, or if you are running the project for the first time, you must ingest them into the vector database.
```bash
python resume_rag.py
```
*What it does: Parses the documents, intelligently chunks them by section, extracts metadata (Name, Skills, Experience), generates vector embeddings, and stores them in ChromaDB.*

### Step 2: Match against a Job Description
Ensure you have a job description `.txt` file inside `data/input/`. Then, run the matching engine and specify the filename as an argument:
```bash
python job_matcher.py job_description_001.txt
```
*What it does: Converts the JD into embeddings, queries ChromaDB, and executes a Hybrid Search (70% Semantic + 30% Keyword). It enforces a strict "Must-Have" experience filter and ranks the top 10 candidates.*

### Step 3: View the Results
Navigate to the `data/output/` folder and open the newly generated `_results.json` file. You will see the Top 10 matches, their final score (0-100), and a human-readable reasoning explaining exactly why the AI selected them.

---

## 📊 Evaluation & Experimentation

Included in the root directory is a Jupyter Notebook:
*   **`notebook.ipynb`**: This is an interactive playground for evaluators. It breaks down the ingestion and retrieval processes step-by-step, measures system latency, and explicitly demonstrates the difference between a "Semantic Only" search and our final "Hybrid Search".

---

## 📚 Technical Documentation
For a deeper dive into how this system was built, please refer to the markdown files in the `docs/` folder:
*   `docs/architecture.md`
*   `docs/context.md`
*   `docs/edgecase.md`
*   `docs/eval.md`
