import json
from django.contrib import messages
from django.shortcuts import redirect, render, HttpResponse
from .decorator import custom_login_required
from .models import *
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import requests
from django.conf import settings
from .forms import *

BASEURL = 'http://127.0.0.1:9000/'
# BASEURL = settings.BASEURL
ENDPOINT = 'micro-service/'

def get_service_plan(service_plan_id):
    try:
        # Attempt to retrieve the service plan object by description
        ms_table = MS_ServicePlan.objects.get(description=service_plan_id)
        return ms_table.ms_id
    except ObjectDoesNotExist:
        return None
    except MultipleObjectsReturned:
        raise ValueError("Multiple service plans found for description: {}".format(service_plan_id))
    except Exception as error:
        return None
    
def call_post_method_without_token(URL,data):
    api_url = URL
    headers = { "Content-Type": "application/json"}
    response = requests.post(api_url,data=data,headers=headers)
    return response


def call_post_method_with_token_v2(URL, endpoint, data, access_token, files=None):
    api_url = URL + endpoint
    headers = {"Authorization": f'Bearer {access_token}'}

    if files:
        response = requests.post(api_url, data=data, files=files, headers=headers)
    else:
        headers["Content-Type"] = "application/json"
        response = requests.post(api_url, data=data, headers=headers)

    if response.status_code in [200, 201]:
        try:
            return {'status_code': 0, 'data': response.json()}
        except json.JSONDecodeError:
            return {'status_code': 1, 'data': 'Invalid JSON response'}
    else:
        try:
            return {'status_code': 1, 'data': response.json()}
        except json.JSONDecodeError:
            return {'status_code': 1, 'data': 'Something went wrong'}

# ====================== Login =============================
def login(request):
    try:
        # Check if the request method is POST
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            payload = {        
                "username" : username,
                "password" : password
            }
            # Convert payload to JSON format
            json_payload = json.dumps(payload)
            ENDPOINT = 'api/token/'
            login_response = call_post_method_without_token(BASEURL+ENDPOINT,json_payload)
            if login_response.status_code == 200:
                login_tokes = login_response.json()
                request.session['user_token']=login_tokes['access']

                return redirect('company_selecting')
            else:
                login_tokes = login_response.json()
                login_error='Invalid Username and Password'
                context={"login_error":login_error}
                return render(request, 'login.html',context)
          
        return render(request, 'login.html')
    except Exception as error:
        return HttpResponse(f'<h1>{error}</h1>')

def company_selecting(request):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('view company') # view company
        if MSID is None:
            print('MISID not found')        
        data = {'ms_id':MSID,'ms_payload':{}} 
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        companies = response['data']
        if request.method == "POST":
            company_id = request.POST.get('companies')
          
            request.session['company_id'] = company_id
            return redirect('dashboard')
            

        return render(request,'company_selecting.html',{'companies':companies})
    except Exception as error:
        return render(request, "error.html", {"error": error})   

        
def dashboard(request):
    return render(request, 'dashboard.html')

# ================== create company =========================
def company_create(request):
    try:
        token = request.session['user_token']
        form = CompanyForm()
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{} }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        if request.method == "POST":
            form = CompanyForm(request.POST,)
            if form.is_valid():
                MSID= get_service_plan('create company')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data   
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/company')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'company.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def company_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view company')
        if MSID is None:
                print('MISID not found')
        payload_form = {"company_id":pk}    
        data = { 'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data'][0]
        form = CompanyForm(initial=master_view)    

        # getting all companies
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MISID not found')
        payload_form = {}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        context={   
            "company_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'company_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def company_edit(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view company')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "company_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
        
        form = CompanyForm(initial=master_type_edit,)

        MSID = get_service_plan('view company')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update company')
            if MSID is None:
                print('MISID not found')
            form = CompanyForm(request.POST,)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['company_id'] = pk    
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/company')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "company_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'company_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def company_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete company')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/company')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# ======================== Customer Management ============================

def customer_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        # getting identification type based on company
        MSID = get_service_plan('view identificationtype') # view_identificationtype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            identification_type_records = response['data']
        else:
            print('Data not found in response')

        form = CustomerForm(identification_type_choice=identification_type_records)

        # getting all customer based on Company 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID, 'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        if request.method == "POST":
            form = CustomerForm(request.POST,identification_type_choice=identification_type_records)
            if form.is_valid():
                MSID = get_service_plan('create customer') # create_customer
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                cleaned_data['dateofbirth'] = cleaned_data['dateofbirth'].strftime('%Y-%m-%d')
                cleaned_data['expiry_date'] = cleaned_data['expiry_date'].strftime('%Y-%m-%d')
                     
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/customer')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'customer.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customer_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view customer')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "customer_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = CustomerForm(initial=master_view)    
        MSID= get_service_plan('view customer')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "customer_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'customer_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customer_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')   
        
        MSID = get_service_plan('view identificationtype')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {'company_id':company_id}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            identification_type_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view customer')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "customer_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CustomerForm(initial=master_type_edit,identification_type_choice=identification_type_records)

        MSID= get_service_plan('view customer')
        if MSID is None:
                print('MISID not found')
        payload_form = { 'company_id':company_id  
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update customer')
            if MSID is None:
                print('MISID not found')
            form = CustomerForm(request.POST,identification_type_choice=identification_type_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['customer_id'] = pk    
                cleaned_data['dateofbirth'] = cleaned_data['dateofbirth'].strftime('%Y-%m-%d')
                cleaned_data['expiry_date'] = cleaned_data['expiry_date'].strftime('%Y-%m-%d')
                cleaned_data['company_id'] = company_id
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/customer')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "customer_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'customer_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customer_delete(request,pk):
    try:
        token = request.session['user_token']

        MSID= get_service_plan('delete customer')
        if MSID is None:
            print('MISID not found') 
        payload_form = { "customer_id":pk}
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/customer')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# =========== customer document =====================
      
def customerdocuments_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
       # getting identification Type
        MSID = get_service_plan('view identificationtype') # view_identificationtype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        # Check if the response contains data
        if 'data' in response:
            document_type_records = response['data']
        else:
            print('Data not found in response')

        # getting all customer data 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            customer_records = response['data']
        else:
            print('Data not found in response')

        form = CustomerdocumentsForm(customer_choice=customer_records,document_type_choice=document_type_records)

        MSID = get_service_plan('view customerdocuments')
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        if request.method == "POST":
            form = CustomerdocumentsForm(request.POST, request.FILES, customer_choice=customer_records, document_type_choice=document_type_records)

            if form.is_valid():
                MSID = get_service_plan('create customerdocuments')
                if MSID is None:
                    print('MISID not found')      
                
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                document_file = request.FILES.get('documentfile')
                files = {'files': (document_file.name, document_file, document_file.content_type)}
                # Remove the file from cleaned_data
                cleaned_data.pop('documentfile', None)  # Ensure that 'documentfile' key is removed if it exists
                data = {'ms_id': MSID, 'ms_payload': json.dumps(cleaned_data)}
                response = call_post_method_with_token_v2(BASEURL, ENDPOINT, data, token, files)   
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('customerdocuments')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'customerdocuments.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    


def customerdocuments_view(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID= get_service_plan('view customerdocuments')
        if MSID is None:
                print('MISID not found')
        payload_form = {"customerdocuments_id":pk}    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = CustomerdocumentsForm(initial=master_view)    
        MSID= get_service_plan('view customerdocuments')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "customerdocuments_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'customerdocuments_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customerdocuments_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
       
        MSID = get_service_plan('view identificationtype')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {'company_id':company_id}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            document_type_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view customerdocuments')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "customerdocuments_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CustomerdocumentsForm(initial=master_type_edit,document_type_choice=document_type_records)

        MSID= get_service_plan('view customerdocuments')
        if MSID is None:
                print('MISID not found')
        payload_form = { 'company_id':company_id      
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update customerdocuments')
            if MSID is None:
                print('MISID not found')
            form = CustomerdocumentsForm(request.POST,document_type_choice=document_type_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['customerdocuments_id'] = pk    
                cleaned_data['uploaded_at'] = cleaned_data['uploaded_at'].strftime('%Y-%m-%d')
                cleaned_data['verified_at'] = cleaned_data['verified_at'].strftime('%Y-%m-%d')
                cleaned_data['company_id'] = company_id 
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/customerdocuments')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "customerdocuments_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'customerdocuments_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customerdocuments_delete(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID= get_service_plan('delete customerdocuments')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "customerdocuments_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/customerdocuments')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


# ==================== Loan Calculater ===================================
def loancalculators_create(request):
    try:
        token = request.session['user_token']
        form = LoancalculatorsForm()
        response = {"data":None}
        if request.method == "POST":
            form = LoancalculatorsForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('calculate repayment schedule')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
          
                cleaned_data['repayment_start_date'] = cleaned_data['repayment_start_date'].strftime('%Y-%m-%d')  
                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
                
                total_payments = sum(item['Installment'] for item in response['data'])
                total_interest = sum(item['Interest'] for item in response['data'])
          
                context = {'form':form,"save":True,'records':response['data'],'total_payments':total_payments,'total_interest':total_interest}
                return render(request, 'loancalculators.html',context)
            else:
                print('errorss',form.errors) 
        context = {'form':form,"save":True,'records':response['data']}
        return render(request, 'loancalculators.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})  

# =================== Loan Application======================
      
def loanapplication_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        # getting customers based on 
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        
        
       
        MSID = get_service_plan('view loantype') # view_loantype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loantype_records = response['data']
        # Check if the response contains data
        if 'data' in response:
            loantype_records = response['data']
        else:
            print('Data not found in response')

        form = LoanapplicationForm(customer_id_choice=customer_id_records,loantype_choice=loantype_records)
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        if request.method == "POST":
            form = LoanapplicationForm(request.POST,customer_id_choice=customer_id_records,loantype_choice=loantype_records)
            if form.is_valid():
                MSID= get_service_plan('create loanapplication') # create_loanapplication
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                cleaned_data['repayment_date'] = cleaned_data['repayment_date'].strftime('%Y-%m-%d')

                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loanapplication')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = {      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'loanapplication.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanapplication_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view loanapplication')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "loanapplication_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = LoanapplicationForm(initial=master_view)    
        MSID= get_service_plan('view loanapplication')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "loanapplication_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'loanapplication_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanapplication_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {'company_id':company_id}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loantype')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {'company_id':company_id}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loantype_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view loanapplication')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "loanapplication_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = LoanapplicationForm(initial=master_type_edit,customer_id_choice=customer_id_records,loantype_choice=loantype_records)

        MSID= get_service_plan('view loanapplication')
        if MSID is None:
                print('MISID not found')
        payload_form = {  'company_id':company_id     
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update loanapplication')
            if MSID is None:
                print('MISID not found')
            form = LoanapplicationForm(request.POST,customer_id_choice=customer_id_records,loantype_choice=loantype_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data  
                cleaned_data['company_id']=company_id        
                cleaned_data['loanapplication_id'] = pk   
                del cleaned_data['repayment_date'] 

                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('loanapplication')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loanapplication_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'loanapplication_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanapplication_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete loanapplication')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"loanapplication_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/loanapplication')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    
# ============================ customer document verification ===========================
def document_varification(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id":company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        context = {'customer_records':response['data']}
        return render(request,"document_verification.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def verify_documents(request,pk): #pk = Customer id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting custiomer data
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MISID not found') 
        payload_form = {"customer_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        customer_data = response['data'][0]

        # getting customer related records
        MSID = get_service_plan('getting verified ducuments') # getting_verified_ducuments
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id":company_id,'customer_id':pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        if request.method == "POST":
            status = request.POST.get("verifying")
            customerdoc = request.POST.getlist("customerdoc") 
   
            if status == "Verified":
                for data in customerdoc:
                    MSID = get_service_plan('customerdoc verification') # customerdoc_verification
                    if MSID is None:
                        print('MISID not found') 
                    payload_form = {"customerdoc_id":data}
                    data = {'ms_id':MSID,'ms_payload':payload_form}
                    json_data = json.dumps(data)
                    response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                    if response['status_code'] == 1:
                        return render(request,'error.html',{'error':str(response['data'])})
                return redirect("document_varification")


        context = {'customer_data':customer_data,'documents':response['data'],'BASEURL':BASEURL}
        return render(request,"document_verify.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

#======================= Loan Application Approval=====================
def loan_approval(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MISID not found') 
        payload_form = {"company_id" : company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        submitted_applications = [app for app in response['data'] if app['application_status'] == 'Submitted']
        approval_applications = [app for app in response['data'] if app['application_status'] == 'Approved']

        context = {'pending_applications':submitted_applications,'approval_applications':approval_applications}
        return render(request,"loan_approval.html",context)
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


def loanapproval(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('loan approval') # loan_approval
        if MSID is None:
            print('MISID not found') 
        payload_form = {'loanapp_id':pk,'approval_status' : "Approved"}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print("response",response)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        return redirect('loan_approval')
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

def deny_application(request):
    try:
        token = request.session['user_token']
        if request.method  == "POST":
            rejecting_reason = request.POST.get("aa")
            loan_applicationid = request.objects.get("aaa")
            MSID = get_service_plan('loan approval') # loan_approval
            if MSID is None:
                print('MISID not found') 
            payload_form = {'loanapp_id':loan_applicationid,'approval_status' : "Rejected",'rejected_reason':rejecting_reason}
            data = {'ms_id':MSID,'ms_payload':payload_form}
            json_data = json.dumps(data)
            response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
            if response['status_code'] == 1:
                return render(request,'error.html',{'error':str(response['data'])})
            return redirect('loan_approval')

    except Exception as error:
        return render(request, "error.html", {"error": error}) 

#======================== Loan Agreement ==========================

def loanagreement_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('getting approved loanapp records') # getting_approved_loanapp_records
        if MSID is None:
            print('MSID not found')
        payload_form = {'company_id':company_id}
        data = {'ms_id': MSID,'ms_payload': payload_form }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})

        loan_details = response['data']
        context = {'loan_details':loan_details, "save":True}
        return render(request, 'loanagreement.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def loanagreement_view(request,pk): # pk = loan id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MSID not found')
        payload_form = {'loan_id':pk}
        data = {'ms_id': MSID,'ms_payload': payload_form }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        
        loan_data = response['data'][0]
        initial_data = {
            'loan_id': loan_data['loan_id'],      # Replace with appropriate logic to get the desired loan
            'loanapp_id': loan_data['loanapp_id']['application_id'],  # Replace with appropriate logic
            'customer_id': loan_data['loanapp_id']['customer_id']['customer_id'],  # Replace with appropriate logic
        }

        form = LoanAgreementForm(initial=initial_data)
        if request.method == "POST":
            form = LoanAgreementForm(request.POST,request.FILES)
            if form.is_valid():
                cleaned_datas = form.cleaned_data
                cleaned_datas['maturity_date'] = cleaned_datas['maturity_date'].strftime('%Y-%m-%d')

                # getting borrower signature
                borrower_signature = request.FILES.get('borrower_signature')

                # getting lender signature
                lender_signature = request.FILES.get('lender_signature')
           
                files = {
                    'borrower_signature': (borrower_signature.name, borrower_signature, borrower_signature.content_type),
                    'lender_signature': (lender_signature.name, lender_signature, lender_signature.content_type)
                }
                MSID = get_service_plan('create loanagreement') # create_loanagreement
                if MSID is None:
                    print('MSID not found')
                payload_form = {'company_id': company_id,'loan_id':loan_data['id'],'loanapp_id': loan_data['loanapp_id']['id'],'customer_id':loan_data['loanapp_id']['customer_id']['id'],
                                'agreement_terms':cleaned_datas['agreement_terms'],'maturity_date':cleaned_datas['maturity_date']}
                data = {'ms_id': MSID,'ms_payload': payload_form }
                json_data = json.dumps(data)
                
                response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
                if response['status_code'] == 1:
                    return render(request,'error.html',{'error':str(response['data'])})
    
            return redirect("loanagreement")
        context={   
            "loanagreement_view_active":"active",
            "View":True,'form':form,'loan_data':loan_data
        }
        return render(request, 'loanagreement_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

# =================== disbursement ==================== 
def view_approvedloan(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting borrower and lender approved agreements with application id
        MSID = get_service_plan('getting approvedloan') # getting_approvedloan
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        approved_loans = response['data']
        context = {'approved_loans':approved_loans}
        return render(request,'disbursement_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})   

def disbursement_create(request,loanid):
    try:
        token = request.session['user_token']

        company_id = request.session.get('company_id')

        # getting company related customers
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')

        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')

        # getting company related loan applications
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            loan_application_records = response['data']
        else:
            print('Data not found in response')

        # getting all Currency
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        # Check if the response contains data
        if 'data' in response:
            currency_records = response['data']
        else:
            print('Data not found in response')
        currency_records = response['data']


        # getting company related bank accounts
        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':1}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        all_banks = response['data']
        # Check if the response contains data
        if 'data' in response:
            all_banks = response['data']
        else:
            print('Data not found in response')
        
        # getting related loan data
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'loan_id':loanid}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        loan_data = response['data'][0]

        initial_data = {
            'customer_id': loan_data['loanapp_id']['customer_id']['customer_id'],
            'loan_id': loan_data['loan_id'],
            'loan_application_id': loan_data['loanapp_id']['application_id'],
            'amount':loan_data['loan_amount']
        }
        
        form = DisbursementForm(initial=initial_data,bank_choice=all_banks,currency_choice=currency_records)
        MSID = get_service_plan('view disbursement')
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        if request.method == "POST":
            form = DisbursementForm(request.POST,bank_choice=all_banks,currency_choice=currency_records)
            if form.is_valid():
                MSID = get_service_plan('create disbursement') # create_disbursement
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data 
                cleaned_data['company_id'] = company_id
                cleaned_data['customer_id'] = loan_data['loanapp_id']['customer_id']['id']
                cleaned_data['loan_id'] = loan_data['id']
                cleaned_data['loan_application_id'] = loan_data['loanapp_id']['id']

                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('view_approvedloan')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
                return redirect("view_approvedloan")
            else:
                print('errorss',form.errors) 
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'disbursement.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def disbursement_view(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('view disbursement')
        if MSID is None:
            print('MISID not found')
        payload_form = {"disbursement_id":pk}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = DisbursementForm(initial=master_view)    

        MSID = get_service_plan('view disbursement')
        if MSID is None:
            print('MISID not found')
        payload_form = {}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "disbursement_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'disbursement_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def disbursement_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loan_application_records = response['data']
        else:
            print('Data not found in response')
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            currency_records = response['data']
        else:
            print('Data not found in response')
        MSID = get_service_plan('view disbursement')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "disbursement_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = DisbursementForm(initial=master_type_edit,company_choice=company_records,customer_id_choice=customer_id_records,loan_application_choice=loan_application_records,currency_choice=currency_records)

        MSID= get_service_plan('view disbursement')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update disbursement')
            if MSID is None:
                print('MISID not found')
            form = DisbursementForm(request.POST,company_choice=company_records,customer_id_choice=customer_id_records,loan_application_choice=loan_application_records,currency_choice=currency_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['disbursement_id'] = pk    
                cleaned_data['disbursement_date'] = cleaned_data['disbursement_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/disbursement')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "disbursement_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'disbursement_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def disbursement_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete disbursement')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "disbursement_id":pk       
        }
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/disbursement')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# ================ loan Repayment =======================
# view all disbursement and procesing loan app ==========================
def view_disbursementloan(request):
    try:
        
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('getting disbursementloans') # getting_disbursementloans
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id' :company_id}
        data = {'ms_id':MSID, 'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        context = {'loan_details':response['data']}
        return render(request,'view_disbursementloan.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})


def view_repaymentschedules(request,pk): # pk = loanapplication id
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        # getting loan deatails with application id
        MSID = get_service_plan('getting repayment schedules') # getting_repayment_schedules
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company_id' : company_id,'loanapp_id' : pk}
        data = {'ms_id':MSID, 'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        schedules = response['data']
       
        # getting repayment schedule with loan application ID
        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MISID not found') 
        payload_form = {'company' : company_id,'loanapp_id' : pk}
        data = {'ms_id':MSID, 'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            
            return render(request,'error.html',{'error':str(response['data'])})
        loan_data = response['data'][0]
        
        # calculate Total amount Due
        print("schedules,schedules",schedules)
        total_installment_amount = sum(item['instalment_amount'] for item in schedules)
        total_paid_amount = sum(item['paid_amount'] for item in schedules)
        
        context = {'schedules':schedules,'loan_data':loan_data,'total_installment_amount':total_installment_amount,'total_paid_amount':total_paid_amount}
        return render(request,'view_repaymentschedules.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})


# =============== Payment Creation ====================     
def payments_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('view loan') # view_loan
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view paymentmethod') # view paymentmethod
        if MSID is None:
            print('MSID not found')
        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            payment_method_records = response['data']
        else:
            print('Data not found in response')

        form = PaymentsForm(loan_id_choice=loanapp_id_records,payment_method_choice=payment_method_records)
        MSID = get_service_plan('view payment') # view_payments
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{'company_id':1}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,"error.html", {"error": response['data']})
        master_view = response['data']

        if request.method == "POST":
            form = PaymentsForm(request.POST,loan_id_choice=loanapp_id_records,payment_method_choice=payment_method_records)
            if form.is_valid():
                MSID = get_service_plan('create payment') # create_payment
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data   
                cleaned_data['company_id']  = company_id
                data = {
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('payments')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'payments.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def payments_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view payments')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "payments_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = PaymentsForm(initial=master_view)    
        MSID= get_service_plan('view payments')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "payments_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'payments_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def payments_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view paymentmethod')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            payment_method_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view payments')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "payments_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = PaymentsForm(initial=master_type_edit,company_choice=company_records,loanapp_id_choice=loanapp_id_records,payment_method_choice=payment_method_records)

        MSID= get_service_plan('view payments')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update payments')
            if MSID is None:
                print('MISID not found')
            form = PaymentsForm(request.POST,company_choice=company_records,loanapp_id_choice=loanapp_id_records,payment_method_choice=payment_method_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['payments_id'] = pk    
                cleaned_data['payment_date'] = cleaned_data['payment_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/payments')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "payments_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'payments_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def payments_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete payments')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "payments_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/payments')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# ========================= Masters =============================
# identification Type 
def identificationtype_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form =IdentificationtypeForm()
        MSID= get_service_plan('view identificationtype') # view_identificationtype
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = IdentificationtypeForm(request.POST)
            if form.is_valid():
                MSID= get_service_plan('create identificationtype')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/identificationtype')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'identificationtype.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def identificationtype_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view identificationtype') # view identificationtype
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "identificationtype_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = IdentificationtypeForm(initial=master_view)  

        
        context={   
            "identificationtype_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'identificationtype_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def identificationtype_edit(request,pk):
    try:
        token = request.session['user_token']
       
        company_id = request.session.get('company_id')

        MSID = get_service_plan('view identificationtype') # view identificationtype
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "identificationtype_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = IdentificationtypeForm(initial=master_type_edit)

        MSID= get_service_plan('view identificationtype') # view_identificationtype
        if MSID is None:
                print('MISID not found')
        payload_form = { }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']


        if request.method == 'POST':
            MSID= get_service_plan('update identificationtype')
            if MSID is None:
                print('MISID not found')
            form = IdentificationtypeForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['identificationtype_id'] = pk    
            
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/identificationtype')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "identificationtype_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'identificationtype_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def identificationtype_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete identificationtype')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "identificationtype_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/identificationtype')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 



#================= Loan Type ==================================
  
def loantype_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form = LoantypeForm()
        MSID = get_service_plan('view loantype')
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = LoantypeForm(request.POST)
            if form.is_valid():
                MSID= get_service_plan('create loantype') # create_loantype
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data   
                cleaned_data['company_id'] = company_id

                data = {'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
           
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('loantype')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = {      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'loantype.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loantype_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view loantype')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "loantype_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = LoantypeForm(initial=master_view)    
        MSID= get_service_plan('view loantype')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "loantype_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'loantype_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loantype_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loantype')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "loantype_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = LoantypeForm(initial=master_type_edit)

        MSID= get_service_plan('view loantype')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update loantype')
            if MSID is None:
                print('MISID not found')
            form = LoantypeForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['loantype_id'] = pk    
                cleaned_data['company_id'] = company_id
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('loantype')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loantype_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'loantype_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loantype_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete loantype')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "loantype_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/loantype')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 





# ================= collateral Type =====================

def collateraltype_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        form=CollateraltypeForm()
        MSID= get_service_plan('view collateraltype') # view_collateraltype
        if MSID is None:
            print('MISID not found')
        data = {
            'ms_id':MSID,
            'ms_payload':{'company_id':company_id}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = CollateraltypeForm(request.POST)
            if form.is_valid():
                MSID= get_service_plan('create collateraltype')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                data = {
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('collateraltype')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'collateraltype.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collateraltype_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view collateraltype')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "collateraltype_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = CollateraltypeForm(initial=master_view)    
        MSID= get_service_plan('view collateraltype')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "collateraltype_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'collateraltype_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collateraltype_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {'company_id':company_id}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view collateraltype')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "collateraltype_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CollateraltypeForm(initial=master_type_edit)

        MSID= get_service_plan('view collateraltype')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update collateraltype')
            if MSID is None:
                print('MISID not found')
            form = CollateraltypeForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['collateraltype_id'] = pk    
                cleaned_data['company_id'] = company_id
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/collateraltype')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "collateraltype_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'collateraltype_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collateraltype_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete collateraltype')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "collateraltype_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/collateraltype')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

#===================== collaterals Create =========================
def collaterals_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')

        MSID = get_service_plan('view loanapplication') # view_loanapplication
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer') # view_customer
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view collateraltype') # view_collateraltype
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            collateral_type_records = response['data']
        else:
            print('Data not found in response')
        form = CollateralsForm(loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)
        MSID = get_service_plan('view collaterals') # view_collaterals
        if MSID is None:
            print('MISID not found')
        data = {
            'ms_id':MSID,
            'ms_payload':{'company_id':company_id}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = CollateralsForm(request.POST, request.FILES,loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)

            if form.is_valid():
                
                MSID= get_service_plan('create collaterals') # create_collaterals
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['valuation_date'] = cleaned_data['valuation_date'].strftime('%Y-%m-%d')
                cleaned_data['company_id'] = company_id
                valuation_report = request.FILES.get('valuation_report')
                files = {'files': (valuation_report.name, valuation_report, valuation_report.content_type)}
                cleaned_data.pop('valuation_report', None)                 
                data = {'ms_id':MSID, 'ms_payload':json.dumps(cleaned_data)}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,data,token,files)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('collaterals')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'collaterals.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collaterals_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view collaterals')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "collaterals_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = CollateralsForm(initial=master_view)    
        MSID= get_service_plan('view collaterals')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "collaterals_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'collaterals_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collaterals_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view collateraltype')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            collateral_type_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view collaterals')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "collaterals_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CollateralsForm(initial=master_type_edit,company_choice=company_records,loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)

        MSID= get_service_plan('view collaterals')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update collaterals')
            if MSID is None:
                print('MISID not found')
            form = CollateralsForm(request.POST,company_choice=company_records,loanapp_id_choice=loanapp_id_records,customer_id_choice=customer_id_records,collateral_type_choice=collateral_type_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['collaterals_id'] = pk    
                cleaned_data['valuation_date'] = cleaned_data['valuation_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/collaterals')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "collaterals_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'collaterals_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def collaterals_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete collaterals')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "collaterals_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/collaterals')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 


#============================= Settings(master functions)============================
# currency 
def currency_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        form = CurrencyForm()
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = CurrencyForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create currency')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data  
                cleaned_data['company_id'] = company_id
                data = {'ms_id':MSID, 'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/currency')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = {'form':form,'records':master_view,"save":True}
        return render(request, 'currency.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def currency_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view currency')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "currency_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = CurrencyForm(initial=master_view)    
        MSID= get_service_plan('view currency')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "currency_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'currency_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def currency_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "currency_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CurrencyForm(initial=master_type_edit)

        MSID= get_service_plan('view currency')
        if MSID is None:
                print('MISID not found')
        payload_form = {'company_id':company_id }
        data = {
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update currency')
            if MSID is None:
                print('MISID not found')
            form = CurrencyForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data  
                cleaned_data['company_id'] = company_id  
                cleaned_data['currency_id'] = pk    
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/currency')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "currency_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'currency_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def currency_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete currency')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "currency_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/currency')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       
# payment method    
def paymentmethod_create(request):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        form = PaymentmethodForm()
        MSID = get_service_plan('view paymentmethod') # view_paymentmethod
        if MSID is None:
            print('MISID not found')
        data = {'ms_id':MSID,'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = PaymentmethodForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create paymentmethod') # create paymentmethod
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['company_id'] = company_id
                     
                data = {
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('paymentmethod')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'paymentmethod.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def paymentmethod_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view paymentmethod')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "paymentmethod_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = PaymentmethodForm(initial=master_view)    
        MSID= get_service_plan('view paymentmethod')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "paymentmethod_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'paymentmethod_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def paymentmethod_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view paymentmethod')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "paymentmethod_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = PaymentmethodForm(initial=master_type_edit)

        MSID = get_service_plan('view paymentmethod') # view_paymentmethod
        if MSID is None:
                print('MISID not found')
        payload_form = {'company_id':company_id}
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update paymentmethod')
            if MSID is None:
                print('MISID not found')
            form = PaymentmethodForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['paymentmethod_id'] = pk    
                cleaned_data['company_id'] = company_id
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('paymentmethod')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "paymentmethod_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'paymentmethod_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def paymentmethod_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete paymentmethod')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "paymentmethod_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/paymentmethod')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# back account creations
def bankaccount_create(request):
    try:
        token = request.session['user_token']

        company_id = request.session.get('company_id')
        form = BankaccountForm()
        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MISID not found')
        data={'ms_id':MSID,'ms_payload':{'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        if request.method == "POST":
            form = BankaccountForm(request.POST)
            if form.is_valid():
                MSID = get_service_plan('create bank account')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data ['company_id'] = company_id
                data={'ms_id':MSID,'ms_payload':cleaned_data} 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('bankaccount')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context = { 'form':form,'records':master_view,"save":True}
        return render(request, 'bankaccount.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def bankaccount_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view bank account')
        if MSID is None:
            print('MISID not found')
        payload_form = {"account_number":pk}    
        data={'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data'][0]
        form = BankaccountForm(initial=master_view)  

        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MISID not found')
        payload_form = {}
        data={'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        context={   
            "bankaccount_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'bankaccount_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def bankaccount_edit(request,pk):
    try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        
        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MISID not found')
        payload_form = {"account_number":pk}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_type_edit = response['data'][0]
 
        form = BankaccountForm(initial=master_type_edit)

        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MISID not found')
        payload_form = {'company_id':company_id}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 1:
            return render(request,'error.html',{'error':str(response['data'])})
        master_view = response['data']

        if request.method == 'POST':
            MSID= get_service_plan('update bank account')
            if MSID is None:
                print('MISID not found')
            form = BankaccountForm(request.POST)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['bank_id'] = pk    
                cleaned_data['company_id'] = company_id
                data = {'ms_id':MSID,'ms_payload':cleaned_data}
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('bankaccount')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "bankaccount_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'bankaccount_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def bankaccount_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete bank account')
        if MSID is None:
            print('MISID not found') 
        payload_form = {"back_id":pk}
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print("****************",response)
        if response['status_code'] == 0:
            messages.info(request, "Well Done..! Your Back Account Deleted..")
            return redirect('bankaccount')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
        return redirect('bankaccount')
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    
# credit scores   
def creditscores_create(request):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        form=CreditscoresForm(company_choice=company_records,customer_id_choice=customer_id_records)
        MSID= get_service_plan('view creditscores')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = CreditscoresForm(request.POST,company_choice=company_records,customer_id_choice=customer_id_records)
            if form.is_valid():
                MSID= get_service_plan('create creditscores')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['retrieved_at'] = cleaned_data['retrieved_at'].strftime('%Y-%m-%d')
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/creditscores')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'creditscores.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def creditscores_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view creditscores')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "creditscores_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = CreditscoresForm(initial=master_view)    
        MSID= get_service_plan('view creditscores')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "creditscores_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'creditscores_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def creditscores_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view creditscores')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "creditscores_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CreditscoresForm(initial=master_type_edit,company_choice=company_records,customer_id_choice=customer_id_records)

        MSID= get_service_plan('view creditscores')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update creditscores')
            if MSID is None:
                print('MISID not found')
            form = CreditscoresForm(request.POST,company_choice=company_records,customer_id_choice=customer_id_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['creditscores_id'] = pk    
                cleaned_data['retrieved_at'] = cleaned_data['retrieved_at'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/creditscores')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "creditscores_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'creditscores_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def creditscores_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete creditscores')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "creditscores_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/creditscores')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 

# =========================== loan offer ========================
def loanoffer_create(request):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            application_id_records = response['data']
        else:
            print('Data not found in response')
        form=LoanofferForm(company_choice=company_records,application_id_choice=application_id_records)
        MSID= get_service_plan('view loan offer')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = LoanofferForm(request.POST,company_choice=company_records,application_id_choice=application_id_records)
            if form.is_valid():
                MSID= get_service_plan('create loan offer')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loanoffer')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'loanoffer.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanoffer_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view loan offer')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "loanoffer_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = LoanofferForm(initial=master_view)    
        MSID= get_service_plan('view loan offer')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "loanoffer_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'loanoffer_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanoffer_edit(request,pk):
    # try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        # Check if the response contains data
        if 'data' in response:
            application_id_records = response['data']
        else:
            print('Data not found in response')

        MSID= get_service_plan('view loan offer')
        if MSID is None:
            print('MISID not found')
        payload_form = {"offer_id":pk}    
        data = {'ms_id':MSID,'ms_payload':payload_form}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_type_edit = response['data'][0]
        
        form = LoanofferForm(initial=master_type_edit,company_choice=company_records,application_id_choice=application_id_records)
        MSID= get_service_plan('view loan offer')
        if MSID is None:
                print('MISID not found')
        payload_form = {}
        data={ 'ms_id':MSID,'ms_payload':payload_form }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']


        if request.method == 'POST':
            MSID= get_service_plan('update loan offer')
            if MSID is None:
                print('MISID not found')
            form = LoanofferForm(request.POST,company_choice=company_records,application_id_choice=application_id_records)
           
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['offer_id'] = pk    
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loanoffer')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loanoffer_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'loanoffer_edit.html',context)   
    # except Exception as error:
    #     return render(request, "error.html", {"error": error})    

def loanoffer_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete loan offer')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "loanoffer_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/loanoffer')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 





def disbursementmethod_create(request):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view disbursement')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            disbursement_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view paymentmethod')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            payment_method_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view bank account')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            bank_account_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            currency_records = response['data']
        else:
            print('Data not found in response')
        form=DisbursementmethodForm(company_choice=company_records,disbursement_id_choice=disbursement_id_records,payment_method_choice=payment_method_records,bank_account_choice=bank_account_records,currency_choice=currency_records)
        MSID= get_service_plan('view disbursementmethod')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = DisbursementmethodForm(request.POST,company_choice=company_records,disbursement_id_choice=disbursement_id_records,payment_method_choice=payment_method_records,bank_account_choice=bank_account_records,currency_choice=currency_records)
            if form.is_valid():
                MSID= get_service_plan('create disbursement method')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/disbursementmethod')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'disbursementmethod.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def disbursementmethod_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view disbursementmethod')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "disbursementmethod_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = DisbursementmethodForm(initial=master_view)    
        MSID= get_service_plan('view disbursementmethod')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "disbursementmethod_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'disbursementmethod_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def disbursementmethod_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view disbursement')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            disbursement_id_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view paymentmethod')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            payment_method_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view bankaccount')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            bank_account_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view currency')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            currency_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view disbursementmethod')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "disbursementmethod_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = DisbursementmethodForm(initial=master_type_edit,company_choice=company_records,disbursement_id_choice=disbursement_id_records,payment_method_choice=payment_method_records,bank_account_choice=bank_account_records,currency_choice=currency_records)

        MSID= get_service_plan('view disbursementmethod')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update disbursementmethod')
            if MSID is None:
                print('MISID not found')
            form = DisbursementmethodForm(request.POST,company_choice=company_records,disbursement_id_choice=disbursement_id_records,payment_method_choice=payment_method_records,bank_account_choice=bank_account_records,currency_choice=currency_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['disbursementmethod_id'] = pk    
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/disbursementmethod')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "disbursementmethod_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'disbursementmethod_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def disbursementmethod_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete disbursementmethod')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "disbursementmethod_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/disbursementmethod')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
    
def customerfeedback_create(request):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        form=CustomerfeedbackForm(customer_id_choice=customer_id_records)
        MSID= get_service_plan('view customerfeedback')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = CustomerfeedbackForm(request.POST,customer_id_choice=customer_id_records)
            if form.is_valid():
                MSID= get_service_plan('create customerfeedback')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['feedback_date'] = cleaned_data['feedback_date'].strftime('%Y-%m-%d')
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/customerfeedback')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'customerfeedback.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customerfeedback_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view customerfeedback')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "customerfeedback_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = CustomerfeedbackForm(initial=master_view)    
        MSID= get_service_plan('view customerfeedback')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "customerfeedback_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'customerfeedback_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customerfeedback_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view customerfeedback')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "customerfeedback_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = CustomerfeedbackForm(initial=master_type_edit,customer_id_choice=customer_id_records)

        MSID= get_service_plan('view customerfeedback')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update customerfeedback')
            if MSID is None:
                print('MISID not found')
            form = CustomerfeedbackForm(request.POST,customer_id_choice=customer_id_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['customerfeedback_id'] = pk    
                cleaned_data['feedback_date'] = cleaned_data['feedback_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/customerfeedback')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "customerfeedback_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'customerfeedback_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def customerfeedback_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete customerfeedback')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "customerfeedback_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/customerfeedback')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       
def loan_create(request):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_records = response['data']
        else:
            print('Data not found in response')
        form=LoanForm(company_choice=company_records,customer_choice=customer_records)
        MSID= get_service_plan('view loan')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = LoanForm(request.POST,company_choice=company_records,customer_choice=customer_records)
            if form.is_valid():
                MSID= get_service_plan('create loan')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['loan_date'] = cleaned_data['loan_date'].strftime('%Y-%m-%d')
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loan')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'loan.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loan_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view loan')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "loan_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = LoanForm(initial=master_view)    
        MSID= get_service_plan('view loan')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "loan_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'loan_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loan_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view loan')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "loan_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = LoanForm(initial=master_type_edit,company_choice=company_records,customer_choice=customer_records)

        MSID= get_service_plan('view loan')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update loan')
            if MSID is None:
                print('MISID not found')
            form = LoanForm(request.POST,company_choice=company_records,customer_choice=customer_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['loan_id'] = pk    
                cleaned_data['loan_date'] = cleaned_data['loan_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loan')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loan_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'loan_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loan_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete loan')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "loan_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/loan')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
 
       
def notifications_create(request):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        form=NotificationsForm(company_choice=company_records,customer_id_choice=customer_id_records)
        MSID= get_service_plan('view notifications')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = NotificationsForm(request.POST,company_choice=company_records,customer_id_choice=customer_id_records)
            if form.is_valid():
                MSID= get_service_plan('create notifications')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/notifications')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'notifications.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def notifications_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view notifications')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "notifications_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = NotificationsForm(initial=master_view)    
        MSID= get_service_plan('view notifications')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "notifications_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'notifications_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def notifications_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view notifications')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "notifications_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = NotificationsForm(initial=master_type_edit,company_choice=company_records,customer_id_choice=customer_id_records)

        MSID= get_service_plan('view notifications')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update notifications')
            if MSID is None:
                print('MISID not found')
            form = NotificationsForm(request.POST,company_choice=company_records,customer_id_choice=customer_id_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['notifications_id'] = pk    
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/notifications')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "notifications_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'notifications_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def notifications_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete notifications')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "notifications_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/notifications')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       
def supporttickets_create(request):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        form=SupportticketsForm(company_choice=company_records,customer_id_choice=customer_id_records)
        MSID= get_service_plan('view supporttickets')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = SupportticketsForm(request.POST,company_choice=company_records,customer_id_choice=customer_id_records)
            if form.is_valid():
                MSID= get_service_plan('create supporttickets')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['resolution_date'] = cleaned_data['resolution_date'].strftime('%Y-%m-%d')
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/supporttickets')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'supporttickets.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def supporttickets_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view supporttickets')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "supporttickets_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = SupportticketsForm(initial=master_view)    
        MSID= get_service_plan('view supporttickets')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "supporttickets_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'supporttickets_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def supporttickets_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view customer')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            customer_id_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view supporttickets')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "supporttickets_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = SupportticketsForm(initial=master_type_edit,company_choice=company_records,customer_id_choice=customer_id_records)

        MSID= get_service_plan('view supporttickets')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update supporttickets')
            if MSID is None:
                print('MISID not found')
            form = SupportticketsForm(request.POST,company_choice=company_records,customer_id_choice=customer_id_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['supporttickets_id'] = pk    
                cleaned_data['resolution_date'] = cleaned_data['resolution_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/supporttickets')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "supporttickets_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'supporttickets_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def supporttickets_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete supporttickets')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "supporttickets_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/supporttickets')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       


  
       
def loanclosure_create(request):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data']
        else:
            print('Data not found in response')
        form=LoanclosureForm(company_choice=company_records,loanapp_id_choice=loanapp_id_records)
        MSID= get_service_plan('view loanclosure')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = LoanclosureForm(request.POST,company_choice=company_records,loanapp_id_choice=loanapp_id_records)
            if form.is_valid():
                MSID= get_service_plan('create loanclosure')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['closure_date'] = cleaned_data['closure_date'].strftime('%Y-%m-%d')
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loanclosure')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'loanclosure.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanclosure_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view loanclosure')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "loanclosure_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = LoanclosureForm(initial=master_view)    
        MSID= get_service_plan('view loanclosure')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "loanclosure_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'loanclosure_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanclosure_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loanapp_id_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view loanclosure')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "loanclosure_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = LoanclosureForm(initial=master_type_edit,company_choice=company_records,loanapp_id_choice=loanapp_id_records)

        MSID= get_service_plan('view loanclosure')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update loanclosure')
            if MSID is None:
                print('MISID not found')
            form = LoanclosureForm(request.POST,company_choice=company_records,loanapp_id_choice=loanapp_id_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['loanclosure_id'] = pk    
                cleaned_data['closure_date'] = cleaned_data['closure_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loanclosure')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loanclosure_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'loanclosure_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loanclosure_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete loanclosure')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "loanclosure_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/loanclosure')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       

       
def repaymentschedule_create(request):
    # try:
        token = request.session['user_token']

        # getting Company records
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
       # getting loan application records
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {'ms_id': MSID,'ms_payload': {}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)
        # Check if the response contains data
        if 'data' in response:
            loan_application_records = response['data']
        else:
            print('Data not found in response')
       
       # getting view payment method
        MSID = get_service_plan('view paymentmethod')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            payment_method_records = response['data']
        else:
            print('Data not found in response')
        form=RepaymentscheduleForm(company_choice=company_records,loan_application_choice=loan_application_records,payment_method_choice=payment_method_records)
        MSID= get_service_plan('view repaymentschedule')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = RepaymentscheduleForm(request.POST,company_choice=company_records,loan_application_choice=loan_application_records,payment_method_choice=payment_method_records)
            if form.is_valid():
                MSID= get_service_plan('create repaymentschedule')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['repayment_date'] = cleaned_data['repayment_date'].strftime('%Y-%m-%d')
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/repaymentschedule')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={'form':form,'records':master_view,"save":True}
        return render(request, 'repaymentschedule.html',context)
    # except Exception as error:
    #     return render(request, "error.html", {"error": error})    

def repaymentschedule_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view repaymentschedule')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "repaymentschedule_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = RepaymentscheduleForm(initial=master_view)    
        MSID= get_service_plan('view repaymentschedule')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "repaymentschedule_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'repaymentschedule_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def repaymentschedule_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loan_application_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view paymentmethod')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            payment_method_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view repaymentschedule')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "repaymentschedule_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = RepaymentscheduleForm(initial=master_type_edit,company_choice=company_records,loan_application_choice=loan_application_records,payment_method_choice=payment_method_records)

        MSID= get_service_plan('view repaymentschedule')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update repaymentschedule')
            if MSID is None:
                print('MISID not found')
            form = RepaymentscheduleForm(request.POST,company_choice=company_records,loan_application_choice=loan_application_records,payment_method_choice=payment_method_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['repaymentschedule_id'] = pk    
                cleaned_data['repayment_date'] = cleaned_data['repayment_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/repaymentschedule')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "repaymentschedule_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'repaymentschedule_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def repaymentschedule_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete repaymentschedule')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "repaymentschedule_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/repaymentschedule')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       

       
def penalties_create(request):
    # try:
        token = request.session['user_token']
        company_id = request.session.get('company_id')
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loan_application_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view repaymentschedule') # view_repaymentschedule
        if MSID is None:
            print('MSID not found')
        data = {'ms_id': MSID,'ms_payload': {'company_id':company_id}}
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            repaymentschedule_id_records = response['data']
        else:
            print('Data not found in response')
        form=PenaltiesForm(loan_application_choice=loan_application_records,repaymentschedule_id_choice=repaymentschedule_id_records)
        MSID= get_service_plan('view penalties')
        if MSID is None:
            print('MISID not found')
   
        data={
            'ms_id':MSID,
            'ms_payload':{}
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        if request.method == "POST":
            form = PenaltiesForm(request.POST,loan_application_choice=loan_application_records,repaymentschedule_id_choice=repaymentschedule_id_records)
            if form.is_valid():
                MSID= get_service_plan('create penalties')
                if MSID is None:
                    print('MISID not found')      
                cleaned_data = form.cleaned_data
                cleaned_data['panalty_date'] = cleaned_data['panalty_date'].strftime('%Y-%m-%d')
                     
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                } 
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                print('response',response)
                if response['status_code'] ==  0:                  
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/penalties')
                else:
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 
        
        context={      
            'form':form,'records':master_view,"save":True
        }
        return render(request, 'penalties.html',context)
    # except Exception as error:
    #     return render(request, "error.html", {"error": error})    

def penalties_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view penalties')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "penalties_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = PenaltiesForm(initial=master_view)    
        MSID= get_service_plan('view penalties')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "penalties_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'penalties_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def penalties_edit(request,pk):
    try:
        token = request.session['user_token']
       
        MSID = get_service_plan('view company')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            company_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view loanapplication')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            loan_application_records = response['data']
        else:
            print('Data not found in response')
       
        MSID = get_service_plan('view repaymentschedule')
        if MSID is None:
            print('MSID not found')

        data = {
            'ms_id': MSID,
            'ms_payload': {}
        }

        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL, ENDPOINT, json_data, token)

        # Check if the response contains data
        if 'data' in response:
            repaymentschedule_id_records = response['data']
        else:
            print('Data not found in response')
        MSID= get_service_plan('view penalties')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "penalties_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = PenaltiesForm(initial=master_type_edit,company_choice=company_records,loan_application_choice=loan_application_records,repaymentschedule_id_choice=repaymentschedule_id_records)

        MSID= get_service_plan('view penalties')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update penalties')
            if MSID is None:
                print('MISID not found')
            form = PenaltiesForm(request.POST,company_choice=company_records,loan_application_choice=loan_application_records,repaymentschedule_id_choice=repaymentschedule_id_records)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['penalties_id'] = pk    
                cleaned_data['panalty_date'] = cleaned_data['panalty_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/penalties')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "penalties_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'penalties_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def penalties_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID = get_service_plan('delete penalties')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "penalties_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/penalties')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       
  

def loancalculators_view(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view loancalculators')
        if MSID is None:
                print('MISID not found')
        payload_form = {
            "loancalculators_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data'][0]
        form = LoancalculatorsForm(initial=master_view)    
        MSID= get_service_plan('view loancalculators')
        if MSID is None:
            print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']

        context={   
            "loancalculators_view_active":"active",
            "form":form,
            "records":master_view,
            "View":True
        }
        return render(request, 'loancalculators_view.html',context)
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loancalculators_edit(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('view loancalculators')
        if MSID is None:
            print('MISID not found')
        payload_form = {
            "loancalculators_id":pk
        }    
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        print('data',response['data'])
        master_type_edit = response['data'][0]
        
        form = LoancalculatorsForm(initial=master_type_edit,)

        MSID= get_service_plan('view loancalculators')
        if MSID is None:
                print('MISID not found')
        payload_form = {       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        master_view = response['data']
        print('master_view',master_view)

        if request.method == 'POST':
            MSID= get_service_plan('update loancalculators')
            if MSID is None:
                print('MISID not found')
            form = LoancalculatorsForm(request.POST,)
            if form.is_valid():
                cleaned_data = form.cleaned_data          
                cleaned_data['loancalculators_id'] = pk    
                cleaned_data['repayment_start_date'] = cleaned_data['repayment_start_date'].strftime('%Y-%m-%d')
                   
                data={
                    'ms_id':MSID,
                    'ms_payload':cleaned_data
                }
                json_data = json.dumps(data)
                response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
                if response['status_code'] == 0:
                    messages.info(request, "Well Done..! Application Submitted..")
                    return redirect('/loancalculators')
                else:
                    # return JsonResponse({'error': 'Failed to save form data'}, status=400)
                    messages.info(request, "Oops..! Application Failed to Submitted..")
            else:
                print('errorss',form.errors) 

        context={   
            "loancalculators_view_active":"active",
            "form":form,
            "edit":True,
            "records":master_view
        }
        return render(request, 'loancalculators_edit.html',context)   
    except Exception as error:
        return render(request, "error.html", {"error": error})    

def loancalculators_delete(request,pk):
    try:
        token = request.session['user_token']
        MSID= get_service_plan('delete loancalculators')
        if MSID is None:
            print('MISID not found') 
        payload_form = {
            "loancalculators_id":pk       
        }
        data={
            'ms_id':MSID,
            'ms_payload':payload_form
        }
        json_data = json.dumps(data)
        response = call_post_method_with_token_v2(BASEURL,ENDPOINT,json_data,token)
        if response['status_code'] == 0:
            
            messages.info(request, "Well Done..! Application Submitted..")
            return redirect('/loancalculators')
        else:
            messages.info(request, "Oops..! Application Failed to Submitted..")
    except Exception as error:
        return render(request, "error.html", {"error": error}) 
       