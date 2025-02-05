import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

class JobSummarizer:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_job_content(self, url):
        """Fetch and parse the job posting content"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            raise Exception(f"Error fetching URL: {str(e)}")

    def summarize_job(self, job_content):
        """Use GPT-4 to summarize the job posting"""
        prompt = f"""Please analyze this job posting and provide a concise summary including:
        1. Job title
        2. Company (if mentioned)
        3. Key responsibilities
        4. Required skills and qualifications
        5. Benefits (if mentioned)
        6. Location/Remote status (if mentioned)

        Job posting content:
        {job_content[:4000]}  # Limiting content length for API constraints
        """

        try:
            response = self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL'),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    def save_summary(self, url, summary):
        """Save the URL and summary to a timestamped file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_summary_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Source URL: {url}\n")
            f.write("=" * 50 + "\n\n")
            f.write(summary)
            
        return filename

def main():
    if len(sys.argv) != 2:
        print("Usage: python JobSummarizer.py <job_posting_url>")
        sys.exit(1)
        
    url = sys.argv[1]
    summarizer = JobSummarizer()
    
    try:
        print("Fetching job posting content...")
        job_content = summarizer.fetch_job_content(url)
        
        print("Generating summary...")
        summary = summarizer.summarize_job(job_content)
        
        print("Saving summary...")
        filename = summarizer.save_summary(url, summary)
        
        print(f"\nSummary saved to: {filename}")
        print("\nSummary:")
        print("=" * 50)
        print(summary)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 