from src.storage import JSONStorage
from src.parser import ResumeParser
from src.matcher import JobMatcher
import os
import sys

def display_menu():
    print("\nResume Job Matcher")
    print("1. Parse resume and find matching jobs")
    print("2. Add new job listing")
    print("3. View all job listings")
    print("4. Initialize sample data")
    print("5. Exit")

def main():
    # Add project root to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    storage = JSONStorage()
    parser = ResumeParser()
    matcher = JobMatcher()

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            resume_path = input("Enter resume file path: ").strip()
            if not os.path.exists(resume_path):
                print("File not found!")
                continue

            print("\nParsing resume...")
            try:
                resume_data = parser.parse_resume(resume_path)
                print(f"Found {len(resume_data['skills'])} skills in resume")

                jobs = storage.get_jobs()
                if not jobs:
                    print("No jobs available. Add some jobs first.")
                    continue

                print("\nFinding best matches...")
                matches = matcher.match_resume_to_jobs(resume_data, jobs)

                print("\nTop 3 Matches:")
                for i, match in enumerate(matches, 1):
                    print(f"\n#{i}: {match['title']} at {match['company']}")
                    print(f"Match Score: {match['score']:.2f}/1.00")
                    print(f"Skills Match: {match['skills_match']}")
                    print("Description:", match['description'][:100] + "...")
            except Exception as e:
                print(f"Error: {str(e)}")

        elif choice == "2":
            print("\nAdd New Job Listing")
            title = input("Job Title: ").strip()
            company = input("Company: ").strip()
            desc = input("Description: ").strip()
            reqs = input("Requirements: ").strip()
            
            if title and company and desc and reqs:
                storage.add_job(title, company, desc, reqs)
                print("Job added successfully!")
            else:
                print("All fields are required!")

        elif choice == "3":
            jobs = storage.get_jobs()
            print(f"\nCurrent Job Listings ({len(jobs)} total):")
            for i, job in enumerate(jobs, 1):
                print(f"\n{i}. {job['title']} at {job['company']}")
                print("Posted:", job.get('posted_date', 'N/A'))
                print("Requirements:", job['requirements'][:50] + "...")

        elif choice == "4":
            confirm = input("This will overwrite existing jobs. Continue? (y/n): ").lower()
            if confirm == 'y':
                storage.initialize_sample_data()
                print("Sample job data initialized!")
            else:
                print("Cancelled")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()