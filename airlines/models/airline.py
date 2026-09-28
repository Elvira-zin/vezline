from django.db import models


class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)
    country = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="airlines/", blank=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

