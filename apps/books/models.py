from django.db import models
from django.conf import settings
from django.core.validators import  MinValueValidator

# Create your models here.
class Books(models.Model):
    title = models.CharField(max_length=200, unique = True)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique = True, blank = True, null = True)
    category = models.CharField(max_length=100, blank =True, default = 'General')
    publisher = models.CharField(max_length=50, blank =True)
    published_at = models.DateField(blank = True, null = True)
    available_copies = models.IntegerField(default = 0, validators = [MinValueValidator(0)])
    total_copies = models.IntegerField(default = 0, validators = [MinValueValidator(0)])
    isDeleted = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add = True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_created', to_field = 'user_id')
    updated_at = models.DateTimeField(null = True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_updated', to_field = 'user_id')
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='books_deleted', to_field = 'user_id')

    def __str__(self):
        return self.title
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['isbn'],
                condition=~models.Q(isbn=None),
                name='unique_isbn_not_null'
            ),
        ]