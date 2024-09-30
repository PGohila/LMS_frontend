from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import *

def common_response(status_code,message=None):
    response = {
        'status_code':status_code,
        'data':f"""{message}""",
    }
    return response

class RegisterServiceplan(APIView):
    def post(self,request,*args,**kwargs):
        try:
            serializer = MS_ServicePlanSerializer(data=request.data)
            if serializer.is_valid():
                ms_id = serializer.validated_data["ms_id"]
                if MS_ServicePlan.objects.filter(ms_id=ms_id).exists():
                    return Response(common_response(status_code=0,message='already registered'),status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response(data = serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        except Exception as error:
            print('error main excepiton ',error)
            return Response(common_response(status_code=0,message=error),status=status.HTTP_404_NOT_FOUND)      

