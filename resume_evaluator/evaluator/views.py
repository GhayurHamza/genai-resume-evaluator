import os
from django.http import JsonResponse
from rest_framework.views import APIView
from .resume_management.processing_pipeline import ResumeProcessor
from .query_management.resume_search_engine import ResumeSearchEngine

class FileUpload(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        UPLOAD_DIR = 'documents'
        if not file:
            return JsonResponse({'error': 'No file provided.'}, status=404)
        if not file.name.endswith('.csv'):
            return JsonResponse({'error': 'Invalid file type. Only CSV files are allowed.'}, status=422)  
        file_path = os.path.join(UPLOAD_DIR, file.name)
        os.makedirs(UPLOAD_DIR, exist_ok=True)  
        try:
            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            processor = ResumeProcessor(file_path)
            processor.process_resumes()
            return JsonResponse({'message': 'File uploaded successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred while uploading the file: {str(e)}'}, status=500)
          
class UserQuery(APIView):
    def get(self, request):
        query = request.query_params.get('query')
        try:
            if not query:
                return JsonResponse({'error': ' Query is required.'}, status=404)
            search_engine = ResumeSearchEngine()
            response = search_engine.get_user_query(query)
            return JsonResponse({'message': 'Result fetched successfully','response':response }, status=200)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred while processing the query: {str(e)}'}, status=500)
