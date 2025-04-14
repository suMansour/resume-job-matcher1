# Resume-Job Matcher 🚀

An intelligent system that parses resumes (PDF/DOCX) and matches them with relevant job listings using **NLP** and **machine learning** techniques.

## Features ✨

- 📄 **Resume Parsing**: Extracts text from PDF and DOCX files
- 🔍 **Skill Extraction**: Identifies technical skills using NLP
- 🤖 **AI Matching**: Combines semantic similarity and exact skill matching
- 📊 **Ranking System**: Scores and ranks top 3 job matches

## How It Works 🧠

1. **Text Extraction**: Converts resumes to raw text
2. **Skill Identification**: Uses spaCy NLP and custom skill patterns
3. **Semantic Analysis**: Creates embeddings using Sentence Transformers
4. **Hybrid Matching**:
   - 60% semantic similarity (understanding context)
   - 40% exact skill matching (hard requirements)
5. **Ranking**: Combines scores to recommend best matches

## Installation ⚙️

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-job-matcher.git
   cd resume-job-matcher
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## Usage 🖥️

1. **Initialize sample data** (optional):

   ```bash
   python main.py
   ```

   Then select option 4 to load sample jobs

2. **Run matching:**
   Place resumes in data/sample_resumes/
   Run python main.py and select option 1
   Enter path to resume file when prompted

3. **Manage jobs:**
   Add new jobs (option 2)
   View current listings (option 3)
