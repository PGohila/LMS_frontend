from django.db import models

# Create your models here.
class MS_ServicePlan(models.Model):
    ms_id = models.CharField(max_length=50)
    serviceplan_id = models.CharField(max_length=50,blank=True,null=True)
    channel_id = models.CharField(max_length=50,blank=True,null=True)
    description =models.CharField(max_length=50)