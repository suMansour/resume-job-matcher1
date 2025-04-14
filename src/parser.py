import re
import spacy
from spacy.matcher import PhraseMatcher
from pdfminer.high_level import extract_text
from docx import Document
from typing import Dict, List

class ResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self._add_skill_patterns()
        
    def _add_skill_patterns(self):
        """Add patterns for common technical skills"""
        self.skill_patterns = [
            "Python", "JavaScript", "Java", "C++", "SQL",
            "Machine Learning", "Deep Learning", "TensorFlow",
            "PyTorch", "AWS", "Docker", "Kubernetes",
            "Git", "React", "Angular", "Node.js", "Django",
            "Flask", "PostgreSQL", "MongoDB", "Linux"
        ]
        
        # Create phrase matcher
        self.matcher = PhraseMatcher(self.nlp.vocab)
        patterns = [self.nlp(text) for text in self.skill_patterns]
        self.matcher.add("SKILLS", patterns)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            return extract_text(pdf_path)
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")

    def extract_text_from_docx(self, docx_path: str) -> str:
        try:
            doc = Document(docx_path)
            return "\n".join([para.text for para in doc.paragraphs if para.text])
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")

    def clean_text(self, text: str) -> str:
        """Normalize whitespace and remove special chars"""
        text = re.sub(r'[^\w\s-]', ' ', text)  # Keep hyphens for compound skills
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower()  # Normalize case for matching

    def parse_resume(self, file_path: str) -> Dict[str, List[str]]:
        # Extract raw text
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError("Only PDF and DOCX files supported")

        # Clean and process text
        clean_text = self.clean_text(text)
        doc = self.nlp(clean_text)
        
        # Extract skills using both NER and pattern matching
        skills = set()
        
        # 1. Get skills from predefined patterns
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            skills.add(doc[start:end].text)
        
        # 2. Get skills from noun phrases containing tech keywords
        tech_keywords = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'ruby', 'kotlin', 'swift',
            'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
            'linux', 'bash', 'powershell', 'devops', 'ci/cd', 'jenkins', 'github', 'gitlab',
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'openai',
            'flask', 'django', 'fastapi', 'spring', 'node.js', 'express', 'react', 'vue', 'angular',
            'html', 'css', 'sass', 'less', 'tailwind', 'bootstrap',
            'rest', 'graphql', 'grpc', 'api', 'microservices', 'serverless',
            'hadoop', 'spark', 'airflow', 'bigquery', 'databricks',
            'tableau', 'power bi', 'excel', 'looker',
            'agile', 'scrum', 'jira', 'confluence',
            'unit testing', 'integration testing', 'pytest', 'junit', 'selenium', 'cypress'
        }
        for chunk in doc.noun_chunks:
            if any(keyword in chunk.text.lower() for keyword in tech_keywords):
                skills.add(chunk.text)
        
        # 3. Get capitalized tech terms (common in resumes)
        for token in doc:
            if token.text.istitle() and token.text.lower() in self.skill_patterns:
                skills.add(token.text)
                
        return {
            "raw_text": clean_text,
            "skills": sorted(list(skills)),  # Convert set to sorted list
            "file_type": file_path.split('.')[-1].upper()
        }