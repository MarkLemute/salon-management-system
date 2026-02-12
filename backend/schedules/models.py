from django.db import models
from backend.staff.models import Staff


class Schedule(models.Model):
    """
    Model representing staff availability schedules.
    Defines time slots when staff members are available.
    """
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField(db_index=True)
    time_slot = models.CharField(max_length=50, help_text='e.g., 10:00-11:00')
    availability_status = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedules'
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        unique_together = ('staff', 'date', 'time_slot')
        ordering = ['date', 'time_slot']
    
    def __str__(self):
        return f"{self.staff.user.username} - {self.date} {self.time_slot}"
