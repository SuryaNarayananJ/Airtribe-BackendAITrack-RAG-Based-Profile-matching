import os
import sys
import re
import json
from pathlib import Path
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass

# Paths
DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
CHROMA_DB_DIR = Path("chroma_db")

def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_chroma_collection():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    return chroma_client.get_collection(name="resumes")

def extract_must_haves(jd_text):
    # Basic parser for 'Must Have: X years' or similar
    must_haves = {"min_experience": 0, "mandatory_skills": []}
    
    # Check for experience
    exp_match = re.search(r"(?:must have|requires|minimum).*?(\d+)\+?\s*years", jd_text, re.IGNORECASE)
    if exp_match:
        must_haves["min_experience"] = int(exp_match.group(1))
        
    # Keywords extraction from JD for our keyword scoring
    common_skills = [
        "python", "java", "aws", "docker", "kubernetes", "machine learning", 
        "react", "c++", "sql", "no-sql", "django", "flask", "fastapi",
        "azure", "gcp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"
    ]
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', jd_text, re.IGNORECASE):
            must_haves["mandatory_skills"].append(skill.title())
            
    return must_haves

def process_job_description(jd_path, embedding_model, collection):
    with open(jd_path, 'r', encoding='utf-8') as f:
        jd_text = f.read()
        
    if not jd_text.strip():
        print(f"Empty JD file: {jd_path.name}")
        return
        
    jd_embedding = embedding_model.encode(jd_text).tolist()
    must_haves = extract_must_haves(jd_text)
    jd_skills = set(must_haves["mandatory_skills"])
    
    # Query ChromaDB (Semantic Search)
    # Query more to allow filtering (e.g. n_results=30) then take Top 10 after hybrid scoring
    try:
        results = collection.query(
            query_embeddings=[jd_embedding],
            n_results=30
        )
    except Exception as e:
        print(f"Error querying ChromaDB: {e}. Is the database populated?")
        return
        
    if not results['documents'] or not results['documents'][0]:
        print("No candidates found in the database.")
        return
        
    candidates = {}
    
    ids = results['ids'][0]
    distances = results['distances'][0] 
    metadatas = results['metadatas'][0]
    documents = results['documents'][0]
    
    for i in range(len(ids)):
        meta = metadatas[i]
        doc = documents[i]
        dist = distances[i]
        
        # Clean the document text for the relevant excerpts
        doc = re.sub(r"^Section: [^\n]+\n", "", doc)
        doc = doc.replace("\n", " ").strip()
        
        # Calculate base semantic score (heuristic mapping of distance to 0-100)
        # Chroma L2 distance mapping (rough heuristic, usually max is ~2.0 for normalized vectors)
        semantic_score = max(0, min(100, 100 - (dist * 40))) 
        
        resume_path = meta['resume_path'].replace('\\', '/')
        
        if resume_path not in candidates:
            candidates[resume_path] = {
                "name": meta['name'],
                "resume_path": resume_path,
                "experience_years": meta.get('experience_years', 0),
                "skills": [s.strip() for s in meta.get('skills', '').split(',') if s.strip()],
                "best_semantic_score": semantic_score,
                "relevant_excerpts": [doc],
                "filtered_out": False
            }
        else:
            # Update if this chunk is a better semantic match
            if semantic_score > candidates[resume_path]["best_semantic_score"]:
                candidates[resume_path]["best_semantic_score"] = semantic_score
            # Add excerpt if unique
            if doc not in candidates[resume_path]["relevant_excerpts"]:
                candidates[resume_path]["relevant_excerpts"].append(doc)
                
    # Evaluate Hybrid Search & Filter
    final_candidates = []
    
    for path, cand in candidates.items():
        # 1. Must-Have Filtering
        if cand["experience_years"] < must_haves["min_experience"]:
            cand["filtered_out"] = True
            
        if cand["filtered_out"]:
            continue
            
        # 2. Keyword Match Score (30%)
        cand_skills = set(cand["skills"])
        if not jd_skills:
            keyword_score = 100 # if no specific keywords identified, give full score
        else:
            matched_skills = cand_skills.intersection(jd_skills)
            keyword_score = (len(matched_skills) / len(jd_skills)) * 100
            
        # 3. Final Scoring (70% Semantic + 30% Keyword)
        final_score = (cand["best_semantic_score"] * 0.7) + (keyword_score * 0.3)
        cand["final_score"] = round(final_score, 2)
        cand["matched_skills"] = list(cand_skills.intersection(jd_skills)) if jd_skills else []
        
        # 4. Match Reasoning
        reasoning = []
        if cand["experience_years"] > 0:
            reasoning.append(f"Has {cand['experience_years']} years of experience.")
        if cand["matched_skills"]:
            reasoning.append(f"Matches critical skills: {', '.join(cand['matched_skills'])}.")
        if cand["best_semantic_score"] > 80:
            reasoning.append("Strong semantic alignment with the job description.")
        elif cand["best_semantic_score"] > 60:
            reasoning.append("Moderate semantic alignment with the job description.")
            
        cand["reasoning"] = " ".join(reasoning)
        if not cand["reasoning"]:
            cand["reasoning"] = "Matched based on general text similarity."
        
        final_candidates.append(cand)
        
    # Sort by final score
    final_candidates.sort(key=lambda x: x["final_score"], reverse=True)
    top_matches = final_candidates[:10]
    
    # Format Output
    output_data = {
        "job_description": jd_path.name,
        "must_haves_identified": must_haves,
        "top_matches": [
            {
                "candidate_name": c["name"],
                "resume_path": c["resume_path"],
                "match_score": c["final_score"],
                "matched_skills": c["matched_skills"],
                "relevant_excerpts": c["relevant_excerpts"][:2], # Limit to top 2 chunks
                "reasoning": c["reasoning"]
            }
            for c in top_matches
        ]
    }
    
    out_file = OUTPUT_DIR / f"{jd_path.stem}_results.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Results saved to {out_file} (Found {len(top_matches)} matches)")

def main():
    print("========================================")
    print("Resume RAG System - Job Matcher Engine")
    print("========================================")
    
    if len(sys.argv) < 2:
        print("Usage: python job_matcher.py <job_description_filename.txt>")
        print("Example: python job_matcher.py job_description_001.txt")
        return
        
    filename = sys.argv[1]
    jd_file = INPUT_DIR / filename
    
    if not jd_file.exists():
        print(f"Error: Could not find '{filename}' in the {INPUT_DIR} directory.")
        return
        
    try:
        embedding_model = get_embedding_model()
        collection = get_chroma_collection()
    except Exception as e:
        print(f"Failed to initialize models/database. Did you run resume_rag.py first? Error: {e}")
        return
        
    print(f"\nProcessing Job Description: {jd_file.name}")
    process_job_description(jd_file, embedding_model, collection)

if __name__ == "__main__":
    main()
