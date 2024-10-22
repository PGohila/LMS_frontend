from django import forms 

	
class CompanyForm(forms.Form):
	name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	phone = forms.CharField( max_length=15,required=True,widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}))
	email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email"}))
	address = forms.CharField(required=True,widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter address"}))
	registration_number = forms.CharField(max_length=50,required=True,widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Registration number"}))
	incorporation_date = forms.DateField( required=False, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))

class IdentificationtypeForm(forms.Form):
	type_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)
		
class CustomerForm(forms.Form):
    is_active = forms.BooleanField(
        required=False,
        label='Active',
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    firstname = forms.CharField(
        max_length=20,
        required=True,
        label='First Name',
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    lastname = forms.CharField(
        max_length=50,
        required=False,
        label='Last Name',
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.TextInput(attrs={"type": "email", "class": "form-control"})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label='Phone Number',
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    address = forms.CharField(
        required=True,
        label='Address',
        widget=forms.Textarea(attrs={"class": "form-control"})
    )
    age = forms.IntegerField(
        required=True,
        label='Age',
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    dateofbirth = forms.DateField(
        required=True,
        label='Date of Birth',
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    customer_income = forms.FloatField(
        required=True,
        label='Customer Income',
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    expiry_date = forms.DateField(
        required=False,
        label='Expiry Date',
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )



class CustomerdocumentsForm(forms.Form):
	is_active = forms.BooleanField(label='Active')
	customer_id = forms.ChoiceField(choices=[],required=True,label="Customer ID", widget=forms.Select(attrs={"class": "form-control"}))
	document_type_id = forms.ChoiceField(choices=[],required=True,label="Document Type", widget=forms.Select(attrs={"class": "form-control"}))
	documentfile = forms.FileField(label='Upload Document')
	description = forms.CharField( required=False, widget=forms.Textarea(attrs={"class": "form-control"}))


	def __init__(self, *args, **kwargs):
		
		customer_list = kwargs.pop('customer_choice', [])
		document_type_list = kwargs.pop('document_type_choice', [])
		super().__init__(*args, **kwargs)

	
		self.fields['customer_id'].choices = [(item['id'], item['customer_id']) for item in customer_list]
		self.fields['document_type_id'].choices = [(item['id'], item['type_name']) for item in document_type_list]

class LoantypeForm(forms.Form):
	DISBURSEMENT_BENEFICIARY_CHOICES = [
        ('pay_self', 'Pay Self'),
        ('pay_milestone', 'Pay Milestone'),
    ]
	is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	loantype = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	interest_rate = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	loan_teams = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	disbursement_beneficiary = forms.ChoiceField(choices=DISBURSEMENT_BENEFICIARY_CHOICES, label="Disbursement Beneficiary", widget=forms.Select(attrs={'class': 'form-control'}))
	min_loan_amt = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	max_loan_amt = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	eligibility = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	collateral_required = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	charges = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		

class LoanapplicationForm(forms.Form):
	TENURE_CHOICES = [
    ('days', 'Days'),
    ('weeks', 'Weeks'),
    ('months', 'Months'),
    ('years', 'Years')
]
	REPAYMENT_SCHEDULE = [('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('annually', 'Annually'),
        ('one_time', 'One Time')]
	REPAYMENT_MODE = [
        ('principal_only', 'Principal Only'),
        ('interest_only', 'Interest Only'),
        ('both', 'Principal and Interest'),
        ('interest_first', 'Interest First, Principal Later'),
        ('principal_end', 'Principal at End, Interest Periodically'),
    ]
	LOAN_CALCILATIONS = [
        ('reducing_balance', 'Reducing Balance Method'),
        ('flat_rate', 'Flat Rate Method'),
        ('constant_repayment', 'Constant Repayment (Amortization)'),
        ('simple_interest', 'Simple Interest'),
        ('compound_interest', 'Compound Interest'),
        ('graduated_repayment', 'Graduated Repayment'),
        ('balloon_payment', 'Balloon Payment'),
        ('bullet_repayment', 'Bullet Repayment'),
        ('interest_first', 'Interest-Only Loans'),
    ]
	INTEREST_BASICS = [
        ('365', '365 Days Basis'),
        ('other', 'Other Basis'),
    ]
	DISBURSEMENT_TYPE = [('one_off', 'One-Off'), ('trenches', 'Trenches')]
	is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	customer_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	loantype_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	loan_amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	disbursement_type = forms.ChoiceField(choices=DISBURSEMENT_TYPE, label="Disbursement Type", widget=forms.Select(attrs={'class': 'form-control'}))
	interest_rate = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	tenure = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	tenure_type = forms.ChoiceField(choices=TENURE_CHOICES, label="Tenure Type", widget=forms.Select(attrs={'class': 'form-control'}))
	repayment_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	loan_calculation_method = forms.ChoiceField(choices=LOAN_CALCILATIONS, label="loan Methods", widget=forms.Select(attrs={'class': 'form-control'}))
	repayment_schedule = forms.ChoiceField(choices=REPAYMENT_SCHEDULE, label="Repayment Schedule", widget=forms.Select(attrs={'class': 'form-control'}))
	repayment_mode = forms.ChoiceField(choices=REPAYMENT_MODE, label="Repayment mode", widget=forms.Select(attrs={'class': 'form-control'}))
	interest_basics = forms.ChoiceField(choices=INTEREST_BASICS, label="interest basics", widget=forms.Select(attrs={'class': 'form-control'}))
	loan_purpose = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	
	def __init__(self, *args, **kwargs):
		customer_id_list = kwargs.pop('customer_id_choice', [])
		loantype_list = kwargs.pop('loantype_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['customer_id'].choices = [(item['id'], f"{item['customer_id']}({item['firstname']} {item['lastname']})") for item in customer_id_list]
		self.fields['loantype_id'].choices = [(item['id'], item['loantype']) for item in loantype_list]

class LoanAgreementForm(forms.Form):
	customer_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	loan_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control"}), required=True)
	loanapp_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	agreement_terms = forms.CharField(required=True,widget=forms.Textarea(attrs={"class": "form-control"}))
	attachment = forms.FileField(required=False, label='Borroewr Signature')
	attachment1 = forms.FileField(required=False,label='Lander Signature')
	maturity_date = forms.DateField(required=False, widget=forms.DateTimeInput(attrs={"class": "form-control","type": "date"}))
	is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))



	
class DisbursementForm(forms.Form):
	DISBURSEMENT_TYPE = [
		('one_off', 'One-Off'), 
		('trenches', 'Trenches')
	]
	DISBURSEMENT_STATUS = [
		('Completed', 'Completed'),
		('Pending', 'Pending'),
	]
	DISBURSEMENT_METHOD = [
		('direct_deposit', 'Direct Deposit'),
		('check', 'Check'),
		('cash', 'Cash'),
		('prepaid_card', 'Prepaid Card'),
		('Third-Party', 'Third-Party')
	]

	
	customer_id = forms.CharField(max_length=50, widget=forms.TextInput(attrs={"class": "form-control","readonly": "readonly"}))
	loan_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control","readonly": "readonly"}))
	loan_application_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"class": "form-control","readonly": "readonly"}))
	amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	disbursement_type = forms.ChoiceField(choices=DISBURSEMENT_TYPE, label="Disbursement Type*", widget=forms.Select(attrs={'class': 'form-control'}))
	disbursement_status = forms.ChoiceField(choices=DISBURSEMENT_STATUS, label="Disbursement Status*", widget=forms.Select(attrs={'class': 'form-control'}))
	disbursement_method = forms.ChoiceField(choices=DISBURSEMENT_METHOD, label="Disbursement Method*", widget=forms.Select(attrs={'class': 'form-control'}))
	currency_id = forms.ChoiceField(choices=[], required=True, label="Currency*", widget=forms.Select(attrs={"class": "form-control"}))
	bank = forms.ChoiceField(choices=[], required=True, label="Bank (Optional)", widget=forms.Select(attrs={"class": "form-control"}))
	notes = forms.CharField(required=False, label="Notes (Optional)", widget=forms.Textarea(attrs={"class": "form-control"}))

	def __init__(self, *args, **kwargs):
		# Extract the additional keyword arguments
		self.customer_id = kwargs.pop('customer_id', None)
		self.loan_id = kwargs.pop('loan_id', None)
		self.loan_application_id = kwargs.pop('loan_application_id', None)

		# Pop the choices for company, currency, and bank

		currency_list = kwargs.pop('currency_choice', [])
		bank_list = kwargs.pop('bank_choice', [])

		# Call the parent class' __init__ method
		super().__init__(*args, **kwargs)

		# Set the choices for the fields
	
		self.fields['currency_id'].choices = [(item['id'], item['name']) for item in currency_list]
		self.fields['bank'].choices = [(item['id'], item['account_number']) for item in bank_list]

        # Optionally set the initial values for customer_id, loan_id, and loan_application_id
		if self.customer_id:
			self.fields['customer_id'].initial = self.customer_id
		if self.loan_id:
			self.fields['loan_id'].initial = self.loan_id
		if self.loan_application_id:
			self.fields['loan_application_id'].initial = self.loan_application_id
	
class CollateraltypeForm(forms.Form):
	CATEGORY = [
		('Tangible','Tangible'), # tangible is physical asset like own property or own bike etc
		('Intangible','Intangible'), # intangible is non-physical assets like parents, trademarks
		('Financial','Financial'), # financial assets like stocks, bonds, and certificates
	]
	
	name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	category = forms.ChoiceField(choices=CATEGORY, label="Category Type", widget=forms.Select(attrs={'class': 'form-control'}))
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		

class CollateralsForm(forms.Form):
	COLLATERAL_STATUS = [
        ('Held', 'Held'),
        ('Released', 'Released'),
        ('Sold', 'Sold'),
    ]
	INSURANCE_STATUS = [
        ('Insured', 'Insured'),
        ('Not insured', 'Not insured'),
    ]
	collateral_type_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	collateral_value = forms.FloatField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	valuation_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	collateral_status = forms.ChoiceField(choices=COLLATERAL_STATUS, label="Collateral status", widget=forms.Select(attrs={'class': 'form-control'}))
	insurance_status = forms.ChoiceField(choices=INSURANCE_STATUS, label="Insurance Status", widget=forms.Select(attrs={'class': 'form-control'}))
	
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control","style": "height: 70px; width: 400px;"}))
	
	def __init__(self, *args, **kwargs):
		collateral_type_list = kwargs.pop('collateral_type_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['collateral_type_id'].choices = [(item['id'], item['name']) for item in collateral_type_list]

class CollateralDocumentForm(forms.Form):
	additional_documents = forms.FileField(label='Additional Document',required=False)
	discription = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))

class PaymentmethodForm(forms.Form):
	method_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
	
		super().__init__(*args, **kwargs)
	

class CurrencyForm(forms.Form):
	
	code = forms.CharField(max_length=3, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	symbol = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	exchange_rate = forms.FloatField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	is_active = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
	
		super().__init__(*args, **kwargs)
	

class CreditscoresForm(forms.Form):
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	customer_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	credit_score = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	retrieved_at = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		customer_id_list = kwargs.pop('customer_id_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['customer_id'].choices = [(item['id'], item['customer_id']) for item in customer_id_list]

class BankaccountForm(forms.Form):
	account_number = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	account_holder_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	bank_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	branch = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	nrfc_number = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	swift_code = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	ifsc_code = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
	
		super().__init__(*args, **kwargs)
		
		
class CustomerfeedbackForm(forms.Form):
	feedback_id = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	customer_id_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	feedback_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	feedback_type = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	subject = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	feedback_status = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		customer_id_list = kwargs.pop('customer_id_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['customer_id_id'].choices = [(item['id'], item['name']) for item in customer_id_list]



class DisbursementmethodForm(forms.Form):
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	disbursement_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"})) 
	payment_method = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	bank_account = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	transaction_reference = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	amount_disbursed = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	currency = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		disbursement_id_list = kwargs.pop('disbursement_id_choice', [])
		payment_method_list = kwargs.pop('payment_method_choice', [])
		bank_account_list = kwargs.pop('bank_account_choice', [])
		currency_list = kwargs.pop('currency_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['disbursement_id'].choices = [(item['id'], item['disbursement_id']) for item in disbursement_id_list]
		self.fields['payment_method'].choices = [(item['id'], item['method_name']) for item in payment_method_list]
		self.fields['bank_account'].choices = [(item['id'], item['account_number']) for item in bank_account_list]
		self.fields['currency'].choices = [(item['id'], item['name']) for item in currency_list]


class LoanForm(forms.Form):
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	loanid = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	customer_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	loan_amount = forms.FloatField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	loan_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	loan_term = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	interest_rate = forms.FloatField( required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	status = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		customer_list = kwargs.pop('customer_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['customer_id'].choices = [(item['id'], item['name']) for item in customer_list]



class NotificationsForm(forms.Form):
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	notification_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	customer_id_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	message = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	status = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	priority = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		customer_id_list = kwargs.pop('customer_id_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['customer_id_id'].choices = [(item['id'], item['name']) for item in customer_id_list]

class SupportticketsForm(forms.Form):
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	ticket_id = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	customer_id_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	subject = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	status = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	priority = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	assigned_to = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	resolution = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	resolution_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		customer_id_list = kwargs.pop('customer_id_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['customer_id_id'].choices = [(item['id'], item['name']) for item in customer_id_list]







class LoanclosureForm(forms.Form):
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	closure_id = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	loanapp_id_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	closure_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	closure_amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	remaining_balance = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	closure_method = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	closure_reason = forms.CharField( required=True, widget=forms.Textarea(attrs={"class": "form-control"}))
	transaction_refference = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		loanapp_id_list = kwargs.pop('loanapp_id_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['loanapp_id_id'].choices = [(item['id'], item['name']) for item in loanapp_id_list]

class LoanofferForm(forms.Form):
	OFFER_STATUS = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	application_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	loanamount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	interest_rate = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	tenure = forms.IntegerField(required=True,widget=forms.NumberInput(attrs={"class": "form-control"}))
	monthly_instalment = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	terms_condition = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	offer_status = forms.ChoiceField(choices=OFFER_STATUS, label="Offer Status", widget=forms.Select(attrs={'class': 'form-control'}))

	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		application_id_list = kwargs.pop('application_id_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['application_id'].choices = [(item['id'], item['application_id']) for item in application_id_list]

class PaymentsForm(forms.Form):
	
	loanid = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	payment_method_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	transaction_reference = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		
		loan_id_list = kwargs.pop('loan_id_choice', [])
		payment_method_list = kwargs.pop('payment_method_choice', [])
		super().__init__(*args, **kwargs)
	
		self.fields['loanid'].choices = [(item['id'], item['loan_id']) for item in loan_id_list]
		self.fields['payment_method_id'].choices = [(item['id'], item['method_name']) for item in payment_method_list]

class RepaymentscheduleForm(forms.Form):
	company_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	loan_application_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	repayment_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	instalment_amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	principal_amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	interest_amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	remaining_balance = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	repayment_status = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	payment_method_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	transaction_id = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		company_list = kwargs.pop('company_choice', [])
		loan_application_list = kwargs.pop('loan_application_choice', [])
		payment_method_list = kwargs.pop('payment_method_choice', [])
		super().__init__(*args, **kwargs)
		self.fields['company_id'].choices = [(item['id'], item['name']) for item in company_list]
		self.fields['loan_application_id'].choices = [(item['id'], item['name']) for item in loan_application_list]
		self.fields['payment_method_id'].choices = [(item['id'], item['name']) for item in payment_method_list]

class PenaltiesForm(forms.Form):
	loan_application_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	repaymentschedule_id_id = forms.ChoiceField(choices=[],required=True, widget=forms.Select(attrs={"class": "form-control"}))
	panalty_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	penalty_amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={"class": "form-control"}))
	penalty_reason = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	payment_status = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	transaction_refference = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):

		loan_application_list = kwargs.pop('loan_application_choice', [])
		repaymentschedule_id_list = kwargs.pop('repaymentschedule_id_choice', [])
		super().__init__(*args, **kwargs)
	
		self.fields['loan_application_id'].choices = [(item['id'], item['application_id']) for item in loan_application_list]
		self.fields['repaymentschedule_id_id'].choices = [(item['id'], item['schedule_id']) for item in repaymentschedule_id_list]

class LoancalculatorsForm(forms.Form):
	TENURE_TYPE = [
		('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')]
	REPAYMENT_SCHEDULE = [('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('halfyearly', 'Half Yearly'),
        ('annually', 'Annually'),
        ('one_time', 'One Time')]
	REPAYMENT_MODE = [
        ('principal_only', 'Principal Only'),
        ('interest_only', 'Interest Only'),
        ('both', 'Principal and Interest'),
        ('interest_first', 'Interest First, Principal Later'),
        ('principal_end', 'Principal at End, Interest Periodically'),
    ]
	CALCULATION_METHOD = [
        ('reducing_balance', 'Reducing Balance Method'),
        ('flat_rate', 'Flat Rate Method'),
        ('constant_repayment', 'Constant Repayment (Amortization)'),
        ('simple_interest', 'Simple Interest'),
        ('compound_interest', 'Compound Interest'),
        ('graduated_repayment', 'Graduated Repayment'),
        ('balloon_payment', 'Balloon Payment'),
        ('bullet_repayment', 'Bullet Repayment'),
        ('interest_first', 'Interest-Only Loans'),
    ]

	loan_amount = forms.FloatField( required=True,label="Loan Amount", widget=forms.NumberInput(attrs={"class": "form-control"}))
	interest_rate = forms.FloatField( required=True,label="Interest Rate", widget=forms.NumberInput(attrs={"class": "form-control"}))
	tenure = forms.IntegerField(required=True,label="Tenure",widget=forms.NumberInput(attrs={"class": "form-control"}))
	tenure_type = forms.ChoiceField(choices=TENURE_TYPE, label="Tenure Type", widget=forms.Select(attrs={'class': 'form-control'}))
	repayment_schedule = forms.ChoiceField(choices=REPAYMENT_SCHEDULE, label="Repayment Schedule", widget=forms.Select(attrs={'class': 'form-control'}))
	repayment_mode = forms.ChoiceField(choices=REPAYMENT_MODE, label="Repayment Mode", widget=forms.Select(attrs={'class': 'form-control'}))
	# interest_basics = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
	loan_calculation_method = forms.ChoiceField(choices=CALCULATION_METHOD, label="Calculation Method", widget=forms.Select(attrs={'class': 'form-control'}))
	repayment_start_date = forms.DateField(required=True, label="Repayment StartDate",widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))

