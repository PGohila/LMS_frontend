from rest_framework import serializers
from .models import *

class MS_ServicePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model= MS_ServicePlan
        fields='__all__'
