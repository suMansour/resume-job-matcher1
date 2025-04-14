import json
import os
from datetime import datetime
from typing import List, Dict


class JSONStorage:
    def __init__(self, file_path='data/jobs.json'):
        self.file_path = file_path
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Create data directory and initialize file with valid JSON if doesn't exist"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({"jobs": []}, f)  # Initialize with empty list
        elif os.path.getsize(self.file_path) == 0:  # If file exists but is empty
            with open(self.file_path, 'w') as f:
                json.dump({"jobs": []}, f)

    def get_jobs(self):
        """Safely read jobs data with error handling"""
        try:
            with open(self.file_path, 'r') as f:
                try:
                    data = json.load(f)
                    return data.get("jobs", [])
                except json.JSONDecodeError:
                    # If file is corrupted, reinitialize it
                    print("Warning: Invalid JSON detected. Reinitializing jobs file.")
                    self._ensure_data_file()
                    return []
        except FileNotFoundError:
            self._ensure_data_file()
            return []

    def add_job(self, title: str, company: str, description: str, requirements: str):
        jobs = self.get_jobs()
        new_job = {
            "id": len(jobs) + 1,
            "title": title,
            "company": company,
            "description": description,
            "requirements": requirements,
            "posted_date": datetime.now().isoformat()
        }
        jobs.append(new_job)
        self._save_all_jobs(jobs)
        return new_job

    def _save_all_jobs(self, jobs: List[Dict]):
        with open(self.file_path, 'w') as f:
            json.dump({"jobs": jobs}, f, indent=2)

    def initialize_sample_data(self):
        sample_jobs = [
            {
                "title": "Software Engineer",
                "company": "TechCorp",
                "description": "Develop and maintain software applications using Python and JavaScript.",
                "requirements": "3+ years Python experience, JavaScript, SQL, CS degree preferred"
            },
            {
                "title": "Data Scientist",
                "company": "DataSystems",
                "description": "Build machine learning models and analyze large datasets.",
                "requirements": "Python, Pandas, Scikit-learn, TensorFlow, Masters in Data Science"
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudSolutions",
                "description": "Implement CI/CD pipelines and manage cloud infrastructure.",
                "requirements": "AWS, Docker, Kubernetes, Terraform, 5+ years experience"
            }
        ]
        
        if not self.get_jobs():
            for job in sample_jobs:
                self.add_job(**job)