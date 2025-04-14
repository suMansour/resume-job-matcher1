from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict
import spacy

class JobMatcher:
    def __init__(self):
        self.model = SentenceTransformer('./all-MiniLM-L6-v2')
        self.skill_db = self._load_skill_db()
        self.nlp = spacy.load("en_core_web_sm")
    
    def _load_skill_db(self) -> Dict[str, List[str]]:
        return {
            "python": ["python", "python3", "py"],
            "java": ["java", "jdk", "jvm"],
            "javascript": ["javascript", "js", "ecmascript"],
            "typescript": ["typescript", "ts"],
            "c++": ["c++", "cpp"],
            "c#": ["c#", "dotnet", ".net"],
            "sql": ["sql", "mysql", "postgresql", "sqlite", "oracle"],
            "mongodb": ["mongodb", "nosql"],
            "aws": ["amazon web services", "aws", "s3", "ec2", "lambda"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["google cloud", "gcp", "bigquery"],
            "docker": ["docker", "containerization"],
            "kubernetes": ["kubernetes", "k8s"],
            "terraform": ["terraform", "iac"],
            "ansible": ["ansible", "configuration management"],
            "linux": ["linux", "unix"],
            "git": ["git", "github", "gitlab"],
            "devops": ["devops", "ci/cd", "jenkins"],
            "machine learning": ["machine learning", "ml", "deep learning"],
            "nlp": ["nlp", "natural language processing"],
            "data science": ["data science", "data analysis"],
            "pandas": ["pandas"],
            "numpy": ["numpy"],
            "scikit-learn": ["scikit-learn", "sklearn"],
            "tensorflow": ["tensorflow", "tf"],
            "pytorch": ["pytorch", "torch"],
            "keras": ["keras"],
            "flask": ["flask"],
            "django": ["django"],
            "fastapi": ["fastapi"],
            "react": ["react", "react.js"],
            "vue": ["vue", "vue.js"],
            "angular": ["angular", "angularjs"],
            "html/css": ["html", "css", "sass", "less"],
            "bootstrap": ["bootstrap"],
            "tailwind": ["tailwind", "tailwindcss"],
            "graphql": ["graphql"],
            "rest": ["rest", "restful api"],
            "hadoop": ["hadoop"],
            "spark": ["spark", "apache spark"],
            "airflow": ["airflow"],
            "tableau": ["tableau"],
            "power bi": ["power bi"],
            "jira": ["jira"],
            "confluence": ["confluence"],
            "testing": ["unit testing", "integration testing", "pytest", "junit", "selenium", "cypress"]
        }
       
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        normalized = set()
        for skill in skills:
            found = False
            skill_lower = skill.lower()
            for std_skill, variants in self.skill_db.items():
                if any(variant in skill_lower for variant in variants):
                    normalized.add(std_skill)
                    found = True
                    break
            if not found and skill.strip():
                normalized.add(skill_lower)
        return list(normalized)
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using both pattern matching and NER"""
        doc = self.nlp(text)
        skills = set()
        
        # Extract using NER
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                skills.add(ent.text.lower())
        
        # Extract using skill database
        text_lower = text.lower()
        for skill, variants in self.skill_db.items():
            if any(variant in text_lower for variant in variants):
                skills.add(skill)
        
        return list(skills)
    
    def match_resume_to_jobs(self, resume_data: Dict, jobs: List[Dict]) -> List[Dict]:
        # Normalize resume skills
        resume_skills = self._normalize_skills(resume_data.get('skills', []))
        
        # Prepare resume text for embedding
        resume_text = (
            f"{resume_data['raw_text']} "
            f"Skills: {', '.join(resume_skills)}"
        )
        
        # Process each job
        job_texts = []
        enhanced_jobs = []
        for job in jobs:
            # Extract and normalize job skills
            job_skills = self._normalize_skills(
                self._extract_skills(f"{job['description']} {job['requirements']}")
            )
            
            # Prepare job text for embedding
            combined_text = (
                f"{job['title']}. {job['description']} "
                f"Requirements: {job['requirements']}"
            )
            
            job_texts.append(combined_text)
            enhanced_jobs.append({
                **job,
                "normalized_skills": job_skills
            })
        
        # Get embeddings for all texts
        texts = [resume_text] + job_texts
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        
        # Calculate similarities between resume and each job
        resume_embedding = embeddings[0:1]
        job_embeddings = embeddings[1:]
        
        similarities = cosine_similarity(
            resume_embedding.cpu().numpy(),
            job_embeddings.cpu().numpy()
        ).flatten()
        
        # Calculate skill overlap scores
        skill_match_info = []
        for job in enhanced_jobs:
            matched_skills = set(resume_skills) & set(job['normalized_skills'])
            total_skills = len(job['normalized_skills']) or 1  # avoid division by zero
            skill_match_info.append({
                "count": len(matched_skills),
                "total": total_skills,
                "ratio": len(matched_skills) / total_skills
            })
        
        # Combine scores (weighted average)
        combined_scores = [
            0.6 * sim + 0.4 * skill_info['ratio']
            for sim, skill_info in zip(similarities, skill_match_info)
        ]
        
        # Get top 3 matches
        top_indices = np.argsort(combined_scores)[-3:][::-1]
        
        # Prepare results
        results = []
        for idx in top_indices:
            job = enhanced_jobs[idx]
            skill_info = skill_match_info[idx]
            
            results.append({
                "title": job['title'],
                "company": job['company'],
                "description": job['description'][:200] + ("..." if len(job['description']) > 200 else ""),
                "score": round(combined_scores[idx], 2),
                "skills_match": f"{skill_info['count']}/{skill_info['total']}",
                "matched_skills": list(set(resume_skills) & set(job['normalized_skills']))
            })
        
        return results