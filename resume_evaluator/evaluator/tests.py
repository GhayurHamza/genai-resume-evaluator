import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_evaluator.settings')
django.setup()
import json
from evaluator.utils import (extract_file_id_from_url,  convert_to_drive_link, 
                             create_vector_embeddings, parse_resume_content, 
                             process_resumes, get_user_query)
from evaluator.models import CandidateProfileData

class Test(unittest.TestCase):
    
    def test_extract_file_id_from_url(self):
        self.assertEqual(extract_file_id_from_url("https://drive.google.com/open?id=12345"), "12345")
        self.assertEqual(extract_file_id_from_url("https://drive.google.com/d/12345/view"), "12345")
        self.assertIsNone(extract_file_id_from_url("https://example.com"))

    def test_convert_to_drive_link(self):
        self.assertEqual(convert_to_drive_link("12345"), "https://drive.google.com/open?id=12345")

    @patch('evaluator.azure_embeddings.CustomAzureOpenAIEmbeddings.get_embedding')
    def test_create_vector_embeddings(self, mock_get_embedding):
        mock_get_embedding.return_value = [0.1, 0.2, 0.3]
        result = create_vector_embeddings("sample text")
        self.assertEqual(result, [0.1, 0.2, 0.3])

    @patch('evaluator.azure_model.CustomAzureChatOpenAI.resume_parser')
    def test_parse_resume_content(self, mock_resume_parser):
        mock_resume_parser.return_value = json.dumps({
            "name": "John Doe",
            "email": "john.doe@example.com",
            "number": "1234567890",
            "degree": "PhD",
            "total_exp": "10 years",
            "skills": "Python, Django",
            "educational_institutions": "Some University",
            "designation": "Senior Developer",
            "summary": "Experienced software developer"
        })
        result = parse_resume_content("resume text")
        expected_result = json.dumps({
            "name": "John Doe",
            "email": "john.doe@example.com",
            "number": "1234567890",
            "degree": "PhD",
            "total_exp": "10 years",
            "skills": "Python, Django",
            "educational_institutions": "Some University",
            "designation": "Senior Developer",
            "summary": "Experienced software developer"
        })
        self.assertEqual(result, expected_result)

    @patch('evaluator.utils.extract_text_from_pdfs_in_folder')
    @patch('evaluator.utils.parse_resume_content')
    @patch('evaluator.utils.create_vector_embeddings')
    @patch('evaluator.utils.convert_to_drive_link')
    @patch('evaluator.models.CandidateProfileData')
    def test_process_resumes(self, mock_candidate_profile, mock_convert_to_drive_link, mock_create_vector_embeddings, mock_parse_resume_content, mock_extract_text_from_pdfs_in_folder):
        # Set up mocks
        mock_extract_text_from_pdfs_in_folder.return_value = [{
            "id": "12345",
            "text": "resume text"
        }]
        mock_parse_resume_content.return_value = json.dumps({
            "name": "John Doe",
            "email": "john.doe@example.com",
            "number": "1234567890",
            "degree": "PhD",
            "total_exp": "10 years",
            "skills": "Python, Django",
            "educational_institutions": "Some University",
            "designation": "Senior Developer",
            "summary": "Experienced software developer"
        })
        mock_create_vector_embeddings.return_value = [0.1, 0.2, 0.3]
        mock_convert_to_drive_link.return_value = "https://drive.google.com/open?id=12345"

        mock_candidate_profile.return_value = MagicMock()
        mock_candidate_profile.return_value.save = MagicMock()

        result = process_resumes('fake_folder_path')
        expected_result = [{
            "name": "John Doe",
            "email": "john.doe@example.com",
            "number": "1234567890",
            "degree": "PhD",
            "years_of_experience": "10 years",
            "skills": "Python, Django",
            "educational_institutions": "Some University",
            "designation": "Senior Developer",
            "resume_link": "https://drive.google.com/open?id=12345",
            "resume_summary": "Experienced software developer",
            "resume_embeddings": [0.1, 0.2, 0.3]
        }]
        self.assertEqual(result, expected_result)

    @patch('evaluator.utils.create_vector_embeddings')
    @patch('evaluator.models.CandidateProfileData.objects.order_by')
    def test_get_user_query(self, mock_order_by, mock_create_vector_embeddings):
        # Set up mocks
        mock_create_vector_embeddings.return_value = [0.1, 0.2, 0.3]
        mock_order_by.return_value = [CandidateProfileData(name="John Doe", email="john.doe@example.com", number="1234567890", resume_link="https://drive.google.com/open?id=12345", resume_summary="Experienced software developer")]

        result = get_user_query("sample text")
        expected_result = [{
            "name": "John Doe",
            "email": "john.doe@example.com",
            "number": "1234567890",
            "resume_link": "https://drive.google.com/open?id=12345",
            "resume_summary": "Experienced software developer"
        }]
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
