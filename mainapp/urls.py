from django.urls import path
from .views import *

urlpatterns = [
    path("",login, name="login"),
    path("company_selecting/",company_selecting, name="company_selecting"),
    path("dashboard/",dashboard, name="dashboard"),

    path('company/', company_create, name='company'),
    path('company-view/<pk>/', company_view, name='company_view'),
    path('company-edit/<pk>/', company_edit, name='company_edit'),
    path('company-delete/<pk>/', company_delete, name='company_delete'),
  
    path('customer/', customer_create, name='customer'),
    path('customer-view/<pk>/', customer_view, name='customer_view'),
    path('customer-edit/<pk>/', customer_edit, name='customer_edit'),
    path('customer-delete/<pk>/', customer_delete, name='customer_delete'),

    path('customerdocuments/', customerdocuments_create, name='customerdocuments'),
    path('customerdocuments-view/<pk>/', customerdocuments_view, name='customerdocuments_view'),
    path('customerdocuments-edit/<pk>/', customerdocuments_edit, name='customerdocuments_edit'),
    path('customerdocuments-delete/<pk>/', customerdocuments_delete, name='customerdocuments_delete'),

    path('loanapplication/', loanapplication_create, name='loanapplication'),
    path('loanapplication-view/<pk>/', loanapplication_view, name='loanapplication_view'),
    path('loanapplication-edit/<pk>/', loanapplication_edit, name='loanapplication_edit'),
    path('loanapplication-delete/<pk>/', loanapplication_delete, name='loanapplication_delete'),

    path('collaterals/', collaterals_create, name='collaterals'),
    path('collaterals-view/<pk>/', collaterals_view, name='collaterals_view'),
    path('collaterals-edit/<pk>/', collaterals_edit, name='collaterals_edit'),
    path('collaterals-delete/<pk>/', collaterals_delete, name='collaterals_delete'),
    
    path('loan/', loan_create, name='loan'),
    path('loan-view/<pk>/', loan_view, name='loan_view'),
    path('loan-edit/<pk>/', loan_edit, name='loan_edit'),
    path('loan-delete/<pk>/', loan_delete, name='loan_delete'),


    path('document_varification/',document_varification,name="document_varification"),
    path('verify_documents/<pk>/',verify_documents,name="verify_documents"),

    path('loan_approval/',loan_approval,name="loan_approval"),
    path('loanapproval/<pk>/',loanapproval,name="loanapproval1"),
    path('deny_application/',deny_application,name="deny_application"),

    
    path('bankaccount/', bankaccount_create, name='bankaccount'),
    path('bankaccount-view/<pk>/', bankaccount_view, name='bankaccount_view'),
    path('bankaccount-edit/<pk>/', bankaccount_edit, name='bankaccount_edit'),
    path('bankaccount-delete/<pk>/', bankaccount_delete, name='bankaccount_delete'),

    path('loanagreement/', loanagreement_create, name='loanagreement'),
    path('loanagreement-view/<pk>/', loanagreement_view, name='loanagreement_view'),
    
    path('view_approvedloan/', view_approvedloan, name='view_approvedloan'),
    path('disbursement/<loanid>/', disbursement_create, name='disbursement'),
    path('disbursement-view/<pk>/', disbursement_view, name='disbursement_view'),
    path('disbursement-edit/<pk>/', disbursement_edit, name='disbursement_edit'),
    path('disbursement-delete/<pk>/', disbursement_delete, name='disbursement_delete'),

    path('collateraltype/', collateraltype_create, name='collateraltype'),
    path('collateraltype-view/<pk>/', collateraltype_view, name='collateraltype_view'),
    path('collateraltype-edit/<pk>/', collateraltype_edit, name='collateraltype_edit'),
    path('collateraltype-delete/<pk>/', collateraltype_delete, name='collateraltype_delete'),

    path('currency/', currency_create, name='currency'),
    path('currency-view/<pk>/', currency_view, name='currency_view'),
    path('currency-edit/<pk>/', currency_edit, name='currency_edit'),
    path('currency-delete/<pk>/', currency_delete, name='currency_delete'),

    path('identificationtype/', identificationtype_create, name='identificationtype'),
    path('identificationtype-view/<pk>/', identificationtype_view, name='identificationtype_view'),
    path('identificationtype-edit/<pk>/', identificationtype_edit, name='identificationtype_edit'),
    path('identificationtype-delete/<pk>/', identificationtype_delete, name='identificationtype_delete'),

    path('loantype/', loantype_create, name='loantype'),
    path('loantype-view/<pk>/', loantype_view, name='loantype_view'),
    path('loantype-edit/<pk>/', loantype_edit, name='loantype_edit'),
    path('loantype-delete/<pk>/', loantype_delete, name='loantype_delete'),

    path('paymentmethod/', paymentmethod_create, name='paymentmethod'),
    path('paymentmethod-view/<pk>/', paymentmethod_view, name='paymentmethod_view'),
    path('paymentmethod-edit/<pk>/', paymentmethod_edit, name='paymentmethod_edit'),
    path('paymentmethod-delete/<pk>/', paymentmethod_delete, name='paymentmethod_delete'),

    

    path('creditscores/', creditscores_create, name='creditscores'),
    path('creditscores-view/<pk>/', creditscores_view, name='creditscores_view'),
    path('creditscores-edit/<pk>/', creditscores_edit, name='creditscores_edit'),
    path('creditscores-delete/<pk>/', creditscores_delete, name='creditscores_delete'),

    path('customerfeedback/', customerfeedback_create, name='customerfeedback'),
    path('customerfeedback-view/<pk>/', customerfeedback_view, name='customerfeedback_view'),
    path('customerfeedback-edit/<pk>/', customerfeedback_edit, name='customerfeedback_edit'),
    path('customerfeedback-delete/<pk>/', customerfeedback_delete, name='customerfeedback_delete'),

 

    path('notifications/', notifications_create, name='notifications'),
    path('notifications-view/<pk>/', notifications_view, name='notifications_view'),
    path('notifications-edit/<pk>/', notifications_edit, name='notifications_edit'),
    path('notifications-delete/<pk>/', notifications_delete, name='notifications_delete'),

    path('supporttickets/', supporttickets_create, name='supporttickets'),
    path('supporttickets-view/<pk>/', supporttickets_view, name='supporttickets_view'),
    path('supporttickets-edit/<pk>/', supporttickets_edit, name='supporttickets_edit'),
    path('supporttickets-delete/<pk>/', supporttickets_delete, name='supporttickets_delete'),

    

    path('loanclosure/', loanclosure_create, name='loanclosure'),
    path('loanclosure-view/<pk>/', loanclosure_view, name='loanclosure_view'),
    path('loanclosure-edit/<pk>/', loanclosure_edit, name='loanclosure_edit'),
    path('loanclosure-delete/<pk>/', loanclosure_delete, name='loanclosure_delete'),

    path('loanoffer/', loanoffer_create, name='loanoffer'),
    path('loanoffer-view/<pk>/', loanoffer_view, name='loanoffer_view'),
    path('loanoffer-edit/<pk>/', loanoffer_edit, name='loanoffer_edit'),
    path('loanoffer-delete/<pk>/', loanoffer_delete, name='loanoffer_delete'),

    path('payments/', payments_create, name='payments'),
    path('payments-view/<pk>/', payments_view, name='payments_view'),
    path('payments-edit/<pk>/', payments_edit, name='payments_edit'),
    path('payments-delete/<pk>/', payments_delete, name='payments_delete'),

    path('disbursementmethod/', disbursementmethod_create, name='disbursementmethod'),
    path('disbursementmethod-view/<pk>/', disbursementmethod_view, name='disbursementmethod_view'),
    path('disbursementmethod-edit/<pk>/', disbursementmethod_edit, name='disbursementmethod_edit'),

    path('view_disbursementloan/', view_disbursementloan, name='view_disbursementloan'),
    path('view_repaymentschedules/<pk>/', view_repaymentschedules, name='view_repaymentschedules'),
    path('repaymentschedule-view/<pk>/', repaymentschedule_view, name='repaymentschedule_view'),
    path('repaymentschedule-edit/<pk>/', repaymentschedule_edit, name='repaymentschedule_edit'),
    path('repaymentschedule-delete/<pk>/', repaymentschedule_delete, name='repaymentschedule_delete'),

    path('penalties/', penalties_create, name='penalties'),
    path('penalties-view/<pk>/', penalties_view, name='penalties_view'),
    path('penalties-edit/<pk>/', penalties_edit, name='penalties_edit'),
    path('penalties-delete/<pk>/', penalties_delete, name='penalties_delete'),

    path('loancalculators/', loancalculators_create, name='loancalculators'),
    path('loancalculators-view/<pk>/', loancalculators_view, name='loancalculators_view'),
    path('loancalculators-edit/<pk>/', loancalculators_edit, name='loancalculators_edit'),
    path('loancalculators-delete/<pk>/', loancalculators_delete, name='loancalculators_delete'),
]
