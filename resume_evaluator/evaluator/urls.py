from django.urls import path
from .views import FileUpload,UserQuery

urlpatterns = [
    path('file_upload/', FileUpload.as_view(), name="file_upload"),
    path('user_query', UserQuery.as_view(), name = 'user_query'),
]
