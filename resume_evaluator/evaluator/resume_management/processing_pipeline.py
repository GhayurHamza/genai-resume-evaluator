import os
import pandas as pd
import fitz
import json
import requests
from ..azure_service.llm_prompt_handler import CustomAzureChatOpenAI
from ..models import CandidateProfileData
from ..azure_service.model_embeddings import CustomAzureOpenAIEmbeddings

class ResumeProcessor:
    def __init__(self, excel_file_path, output_directory='resume_data'):
        self.excel_file_path = excel_file_path
        self.output_directory = output_directory
        os.makedirs(self.output_directory, exist_ok=True)
    
    def extract_file_id_from_url(self, url):
        if 'drive.google.com' in url:
            if 'open?id=' in url:
                return url.split('open?id=')[1]
            elif '/d/' in url:
                return url.split('/d/')[1].split('/')[0]
        return None

    def download_resumes_from_excel(self):
        df = pd.read_excel(self.excel_file_path)
        name_column = df.columns[3]
        url_column = df.columns[-1]  
        for index, row in df.iterrows():
            name = row[name_column]
            url = row[url_column]           
            if pd.notna(url) and pd.notna(name):
                file_id = self.extract_file_id_from_url(url)
                if file_id:
                    download_url = f"https://drive.google.com/uc?id={file_id}"               
                    output_file = os.path.join(self.output_directory, f"{name}_{file_id}.pdf")              
                    try:
                        response = requests.get(download_url, stream=True)
                        response.raise_for_status()                    
                        with open(output_file, 'wb') as file:
                            file.write(response.content)                  
                    except requests.HTTPError as http_err:
                        print(f"HTTP error occurred for row {index + 1}: {http_err}")
                    except Exception as err:
                        print(f"Other error occurred for row {index + 1}: {err}")
                    else:
                        print(f"Downloaded and saved {output_file}")

    def extract_text_from_pdfs(self):
        try:
            if not os.path.isdir(self.output_directory):
                return json.dumps([{"id": None, "text": f"Directory does not exist: {self.output_directory}"}])
            pdf_texts = []
            pdf_count = 0  
            for filename in os.listdir(self.output_directory):
                if filename.endswith('.pdf'):
                    pdf_count += 1
                    if pdf_count > 70:
                        break
                    base_name = os.path.splitext(filename)[0]
                    parts = base_name.split('_', 1) 
                    doc_id = parts[1] if len(parts) > 1 else base_name               
                    file_path = os.path.join(self.output_directory, filename)
                    document = fitz.open(file_path)
                    text = ""
                    for page_num in range(len(document)):
                        page = document.load_page(page_num)
                        text += page.get_text()          
                    document.close()              
                    pdf_texts.append({
                        "id": doc_id,
                        "text": text if text else "No text found in the PDF."
                    })
            return pdf_texts
        except Exception as e:
            return json.dumps([{"id": None, "text": f"An error occurred: {e}"}])

    def convert_to_drive_link(self, file_id):
        base_url = "https://drive.google.com/open?id="
        return f"{base_url}{file_id}"

    def create_vector_embeddings(self, texts_item):
        embeddings = CustomAzureOpenAIEmbeddings()
        embedded_vectors = embeddings.get_embedding(texts_item)
        return embedded_vectors

    def parse_resume_content(self, resume_text_content):
        llm = CustomAzureChatOpenAI(temperature=0)
        parsed_resume = llm.resume_parser(resume_text_content)
        return parsed_resume

    def process_resumes(self):
        self.download_resumes_from_excel()
        pdf_texts = self.extract_text_from_pdfs()
        results = []
        for item in pdf_texts:
            resume_id = item["id"]
            resume_text_content = item["text"]  
            parsed_resume = self.parse_resume_content(resume_text_content)
            parsed_resume = json.loads(parsed_resume)
            embeddings = self.create_vector_embeddings(parsed_resume["summary"])    
            resume_link = self.convert_to_drive_link(resume_id)       
            result = {
                "name": parsed_resume["name"],
                "email": parsed_resume["email"],
                "number": parsed_resume["number"],
                "degree": parsed_resume["degree"],
                "years_of_experience": parsed_resume["total_exp"],
                "skills": parsed_resume["skills"],
                "educational_institutions": parsed_resume["educational_institutions"],
                "designation": parsed_resume["designation"],
                "resume_link": resume_link,
                "resume_summary": parsed_resume["summary"],
                "resume_embeddings": embeddings
            }
            CandidateProfileData.objects.create(**result)
            results.append(result) 
        return results
