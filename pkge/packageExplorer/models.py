from django.contrib.auth.models import User
from django.db import models

class Package(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField('Tag', related_name='packages')
    thumbnail = models.ImageField(upload_to='thumbnails/')
    external_link = models.URLField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='packages', null=True, blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Submission(models.Model):
    package = models.OneToOneField(Package, on_delete=models.CASCADE, related_name='submission')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)