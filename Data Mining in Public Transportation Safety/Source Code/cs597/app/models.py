from django.db import models

# Create your models here.

class City(models.Model):
    zip = models.CharField(max_length=10)
    name = models.CharField(blank=True, max_length=50)
    county = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=50)
    longitude = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)

class sTweet(models.Model):
    tid = models.AutoField(primary_key=True)
    text = models.TextField(blank=True, max_length=280)
    longitude = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    address = models.CharField(blank=True, max_length=64)
    signal = models.CharField(blank=True, max_length=10)
    create_at = models.DateTimeField(null=True)
