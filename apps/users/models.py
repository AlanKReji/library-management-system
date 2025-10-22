from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Users(AbstractUser):   
    email = models.EmailField(unique=True) 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        USER = "USER", "User"

    base_role = Role.USER
    role = models.CharField(max_length=50, choices=Role.choices, default=base_role)
    
    user_id = models.CharField(max_length=10, unique=True, editable=False)
    
    isDeleted = models.BooleanField(default = False)
    
    created_at = models.DateTimeField(auto_now_add = True) 
    updated_at = models.DateTimeField(null=True, blank=True) 
    deleted_at = models.DateTimeField(null=True, blank=True) 
    
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='users_created_by', to_field='user_id')
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='users_updated_by', to_field='user_id')
    deleted_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='users_deleted_by', to_field='user_id')


    def save(self, *args, **kwargs):
        if not self.user_id:
            next_id = Users.objects.count() + 1
            self.user_id = f"USER-{next_id:03d}"
            
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            
        elif self.role == self.Role.LIBRARIAN:
            self.is_staff = True
            self.is_superuser = False
            
        else:
            self.is_staff = False
            self.is_superuser = False
            
        if not self.pk:
            self.role = self.base_role
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} ({self.get_role_display()})"