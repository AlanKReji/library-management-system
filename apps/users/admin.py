from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users
from .forms import AdminUserCreationForm, AdminUserChangeForm

# --- Define the Custom Admin Interface ---

class CustomUserAdmin(UserAdmin):
    # Use your custom forms for adding and changing users
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    
    # Fields to display in the list view of the admin site
    list_display = ('user_id', 'email', 'username', 'role', 'is_staff', 'is_active')
    
    # Fields to use on the "change user" page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Custom Audit', {'fields': ('user_id', 'isDeleted', 'created_by', 'updated_by', 'deleted_by')}),
    )
    
    # Fields to use on the "add user" page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'password', 'password2')}
        ),
    )
    
    # Ensure all filtering and searching works on the custom fields
    search_fields = ('email', 'username', 'user_id')
    ordering = ('email',)

# --- Register the Model with the Custom Admin Interface ---
admin.site.register(Users, CustomUserAdmin)