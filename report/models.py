from datetime import date
from email import message
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Report(models.Model):
    report_by       =   models.ForeignKey(User, on_delete=models.CASCADE, related_name='reporter')
    reported_to     =   models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_to')
    message         =   models.TextField(blank=False)
    date            =   models.DateTimeField(auto_now_add=True)
    completed       =   models.BooleanField(default=False)

    def __str__(self):
        return f'{self.report_by.full_name} reported {self.reported_to.full_name}'