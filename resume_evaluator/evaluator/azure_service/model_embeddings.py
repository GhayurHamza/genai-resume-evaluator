import os
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class CustomAzureOpenAIEmbeddings(AzureOpenAIEmbeddings):
    def __init__(self):
        VECTORIZATION_DEPLOYMENT_NAME = os.getenv("VECTORIZATION_DEPLOYMENT_NAME")
        VECTORIZATION_MODEL_NAME = os.getenv("VECTORIZATION_MODEL_NAME")
        VECTORIZATION_USER_ID = os.getenv("VECTORIZATION_USER_ID")
 
        super().__init__(
            deployment=VECTORIZATION_DEPLOYMENT_NAME,
            chunk_size=1,
            model=VECTORIZATION_MODEL_NAME,
            default_headers={"User-Id": VECTORIZATION_USER_ID}
        )

    def get_embedding(self, text):
        response = self.embed_query(text)
        return response
