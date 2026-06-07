import os
import re
from pathlib import Path
try:
    from pypdf import PdfReader
except ImportError:
    pass # Will be installed by user
try:
    import docx
except ImportError:
    pass # Will be installed by user
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass # Will be installed by user

# Define paths
DATA_DIR = Path("data")
RESUMES_DIR = DATA_DIR / "resumes"
CHROMA_DB_DIR = Path("chroma_db")

def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_chroma_collection():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    return chroma_client.get_or_create_collection(name="resumes")

def extract_text_from_file(file_path):
    ext = file_path.suffix.lower()
    text = ""
    if ext == '.pdf':
        try:
            reader = PdfReader(str(file_path))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Failed to read PDF {file_path.name}: {e}")
    elif ext == '.docx':
        doc = docx.Document(str(file_path))
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print(f"Unsupported file format: {ext}")
    return text

def chunk_resume(text):
    # Intelligent chunking based on typical resume sections
    # We will split text where common section headers appear
    sections = [
        "summary", "education", "experience", "work experience", 
        "skills", "projects", "certifications", "work history", "employment"
    ]
    
    # Matches a line that contains mostly just the section header (case-insensitive)
    pattern = r"(?i)^\s*(" + "|".join(sections) + r")\s*:?\s*$"
    
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_header = "General Information"
    
    for line in lines:
        if re.match(pattern, line):
            if current_chunk:
                chunks.append({"header": current_header, "text": "\n".join(current_chunk).strip()})
            # Clean up the header to standard format (e.g., "WORK EXPERIENCE:" -> "Work Experience")
            current_header = re.sub(r"[:\s]+$", "", line.strip()).title()
            current_chunk = []
        else:
            if line.strip():
                current_chunk.append(line)
    
    if current_chunk:
        chunks.append({"header": current_header, "text": "\n".join(current_chunk).strip()})
        
    return chunks

def extract_metadata(text):
    # Basic rule-based metadata extraction
    metadata = {
        "name": "Unknown",
        "skills": [],
        "experience_years": 0,
        "education": "Unknown"
    }
    
    # Try to guess name from first non-empty line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        metadata["name"] = lines[0][:50] # assume first line is the name
        
    # Extract years of experience (naive approach looking for "X years")
    exp_match = re.search(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", text, re.IGNORECASE)
    if exp_match:
        metadata["experience_years"] = int(exp_match.group(1))
        
    # Extract common skills
    common_skills = [
        "python", "java", "aws", "docker", "kubernetes", "machine learning", 
        "react", "c++", "sql", "no-sql", "django", "flask", "fastapi",
        "azure", "gcp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"
    ]
    found_skills = []
    for skill in common_skills:
        # Look for whole word matches
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.append(skill.title())
    metadata["skills"] = ", ".join(found_skills)
    
    # Check education
    if re.search(r"(bachelor|b\.s\.|b\.a\.|master|m\.s\.|m\.a\.|phd|degree)", text, re.IGNORECASE):
        metadata["education"] = "Degree Inferred"
        
    return metadata

def process_resumes():
    print("Starting Resume Processing...")
    if not RESUMES_DIR.exists():
        print(f"Directory {RESUMES_DIR} not found. Please create it and add resumes.")
        return
        
    resume_files = list(RESUMES_DIR.glob('*.*'))
    if not resume_files:
        print(f"No resumes found in {RESUMES_DIR}")
        return
        
    embedding_model = get_embedding_model()
    collection = get_chroma_collection()
        
    for file_path in resume_files:
        if file_path.suffix.lower() not in ['.pdf', '.docx', '.txt']:
            continue
            
        print(f"Processing: {file_path.name}")
        text = extract_text_from_file(file_path)
        if not text.strip():
            print(f"Could not extract text from {file_path.name}")
            continue
            
        metadata = extract_metadata(text)
        chunks = chunk_resume(text)
        
        print(f"  -> Extracted {len(chunks)} chunks. Metadata: {metadata}")
        
        # Insert each chunk into ChromaDB
        for i, chunk in enumerate(chunks):
            chunk_text = chunk['text']
            if not chunk_text:
                continue
                
            # Generate ID for the chunk
            chunk_id = f"{file_path.stem}_chunk_{i}"
            
            # Combine header with text for better semantic context
            content_to_embed = f"Section: {chunk['header']}\n{chunk_text}"
            
            # Generate embeddings
            embedding = embedding_model.encode(content_to_embed).tolist()
            
            # Store in ChromaDB
            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[content_to_embed],
                metadatas=[{
                    "resume_path": str(file_path),
                    "name": metadata["name"],
                    "skills": metadata["skills"],
                    "experience_years": metadata["experience_years"],
                    "education": metadata["education"],
                    "chunk_header": chunk["header"]
                }]
            )
            
    print("Processing Complete. Embeddings stored in ChromaDB.")

def main():
    print("========================================")
    print("Resume RAG System - Indexing Resumes")
    print("========================================")
    process_resumes()

if __name__ == "__main__":
    main()
