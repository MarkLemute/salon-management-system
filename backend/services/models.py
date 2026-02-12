from django.db import models


class Service(models.Model):
    """
    Model representing salon services.
    Examples: Haircut, Braiding, Manicure, Pedicure, etc.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text='Duration in minutes')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
