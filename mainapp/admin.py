from django.contrib import admin
from .models import *

class MS_ServicePlanAdmin(admin.ModelAdmin):
    list_display=['ms_id','description']
admin.site.register(MS_ServicePlan,MS_ServicePlanAdmin)