from django.db import models
from django.core.validators import  MinValueValidator

# Create your models here.
class Books(models.Model):
    title = models.CharField(max_length=200, unique = True)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique = True, blank = True, null = True)
    category = models.CharField(max_length=100, default = 'General')
    publisher = models.CharField(max_length=50, blank =True)
    published_at = models.DateField(blank = True, null = True)
    available_copies = models.IntegerField(default = 0, validators = [MinValueValidator(0)])
    total_copies = models.IntegerField(default = 0, validators = [MinValueValidator(0)])
    isDeleted = models.BooleanField(default = False)
    created_at = models.DateField(auto_now_add = True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_created')
    updated_at = models.DateField(auto_now = True)
    # updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_updated')
    deleted_at = models.DateField(auto_now = True)
    # deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_deleted')

    def __str__(self):
        return self.title