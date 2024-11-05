from django.db import models
from pgvector.django import VectorField

class CandidateProfileData(models.Model):
    candidate_id = models.AutoField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    degree=models.TextField()
    number = models.CharField(max_length=20)
    years_of_experience = models.TextField()
    skills = models.TextField() 
    educational_institutions= models.TextField()
    designation= models.TextField()
    resume_link= models.TextField()
    resume_summary = models.TextField()
    resume_embeddings =VectorField(dimensions=1536)

    class Meta:
        db_table = 'candidates_profile'
