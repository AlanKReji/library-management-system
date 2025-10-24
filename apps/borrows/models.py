from django.db import models
from django.conf import settings
from apps.books.models import Books
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

def get_due_date():
    return timezone.now() + timedelta(days=14)  # Assuming 14 days borrow period; adjust as needed

class Borrow(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='borrows')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=get_due_date)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def calculate_fine(self):
        if self.return_date and self.status == 'RETURNED':
            overdue_days = max(0, (self.return_date.date() - self.due_date.date()).days)
            if overdue_days > 0:
                self.fine_amount = Decimal('50.00') + (Decimal('5.00') * overdue_days)
            else:
                self.fine_amount = Decimal('0.00')
        return self.fine_amount

    def save(self, *args, **kwargs):
        if self.return_date and self.status != 'RETURNED':
            self.status = 'RETURNED'
            self.calculate_fine()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.user_id} borrowed {self.book.title} (Status: {self.get_status_display()})"
