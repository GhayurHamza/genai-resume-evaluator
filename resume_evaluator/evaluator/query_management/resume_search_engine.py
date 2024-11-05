from ..azure_service.model_embeddings import CustomAzureOpenAIEmbeddings
from ..models import CandidateProfileData
from pgvector.django import CosineDistance

class ResumeSearchEngine:
    def __init__(self):
        self.embeddings_service = CustomAzureOpenAIEmbeddings()

    def create_vector_embeddings(self, texts_item):
        embedded_vectors = self.embeddings_service.get_embedding(texts_item)
        return embedded_vectors

    def get_user_query(self, text):
        embeddings = self.create_vector_embeddings(text)
        search_output = CandidateProfileData.objects.order_by(CosineDistance('resume_embeddings', embeddings))[:5]
        results = []
        emails = set()  
        for output in search_output:
            if output.email not in emails:
                emails.add(output.email)
                result = { 
                    "name": output.name,
                    "email": output.email,
                    "number": output.number,
                    "resume_link": output.resume_link,
                    "resume_summary": output.resume_summary
                }
                results.append(result)
        return results
