from django.db import models

class Taxe(models.Model):
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    service_charge_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Don't delete just update current Tax percentage {self.tax_percentage}% and Service percentage is {self.service_charge_percentage}%."
