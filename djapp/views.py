# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 22:55:42 2019

"""
from sre_constants import SUCCESS
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .auth_login import login_redirect, require_forgotpassword_access
from djapp.plugins.login import user_auth, signup, check_email_exists, send_verification_code_email,password_reset_successful
from djapp.plugins.login import post_timestamp
from .plugins.History import get_history, get_billing_history
from djapp.plugins.Home_Page import load_all_available_services, load_all_available_sizes, file_processing, get_balance, \
    on_continue_pressed, send_request, get_FAQs, get_user_Name, post_client_id, get_user_wallet, load_services_with_prices_single_label, send_request_for_single_label
from djapp.plugins.Home_Page import single_label as sl
from djapp.plugins.contact_us import contactus
from settings.views import add_record, get_records, make_a_new_default_address, make_address_as_default
from djapp.plugins.config import config3
import pyrebase
from .plugins.blog_info import blog_info

import json

import pandas
import numpy as np
from djapp.plugins.domain_val import domain_val,img_logo_link
import random

domain = domain_val()
logo_link = img_logo_link()


################################################################
# Authentication Views
################################################################


def login_views(request):
    message = False
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass']
        try:
            get_auth = user_auth(email, password)
        except:
            get_auth =False

        if get_auth:
            token = get_auth.get('idToken')
            if token:
                request.session['uid'] = str(token)
                request.session['email'] = email
                if (get_auth.get('displayName') == ''):
                    request.session['name'] = get_user_Name(get_auth.get('localId'))
                else:
                    request.session['name'] = get_auth.get('displayName')

                user_id = get_auth.get('localId')
                request.session['user_auth'] = user_id
                request.session['balance'] = get_balance(user_id)
                request.session.set_expiry(10800)
                post_timestamp(get_auth.get('localId'))

                try:
                    client_ip = request.META['REMOTE_ADDR']
                    post_client_id(user_id, str(client_ip))
                except Exception:
                    pass
                try:
                    default_address, _ = get_records("addresses", user_id)
                except Exception:
                    default_address = None

                request.session['is_default_address'] = False
                if default_address:
                    request.session['is_default_address'] = True
                
                # Extract the user's UTC offset from the form data
                try:
                    user_utc_offset = int(request.POST.get('user_utc_offset', 0)) / 60
                    request.session['time_difference'] = user_utc_offset
                    print(user_utc_offset)
                except:
                    request.session['time_difference'] = 0

                return redirect(reverse('djapp:dashboard'))
            else:
                message = "Wrong E-Mail or Password. If you face a problem with signing in please contact us at support@"+domain+".com"
        else:
            message = "Wrong E-Mail or Password. If you face a problem with signing in please contact us at support@"+domain+".com"
    
    return render(request, 'accounts/login_2.html', locals())


def signup_views(request):
    try: ip_add = request.META.get('HTTP_X_FORWARDED_FOR')
    except: ip_add = 0
    message = False
    if request.method == "POST":
        email = request.POST['email']
        name = request.POST['name'].capitalize()
        customer_pass = request.POST['customer_pass']
        request.session['time_difference'] = 0
        try:
            rrr = signup(email, name, ip_add, customer_pass)
            if rrr:
                message = "Registration Successful. Kindly review your email & spam folder. Thank you."
                success_modal = True

                #login the customer directly to the system
                try:
                    get_auth = user_auth(email, customer_pass)
                    if get_auth:
                        #print("auth: "+get_auth)
                        token = get_auth.get('idToken')
                        if token:
                            request.session['uid'] = str(token)
                            if (get_auth.get('displayName') == ''):
                                # request.session['name'] = get_auth.get('email').split('@')[0]
                                request.session['name'] = get_user_Name(get_auth.get('localId'))
                            else:
                                request.session['name'] = get_auth.get('displayName')
                            user_id = get_auth.get('localId')
                            request.session['user_auth'] = user_id
                            request.session['balance'] = get_balance(user_id)
                            request.session.set_expiry(10800)
                            post_timestamp(get_auth.get('localId'))
                            try:
                                client_ip = request.META['REMOTE_ADDR']
                                post_client_id(user_id, str(client_ip))
                            except:
                                pass
                            
                            try:
                                default_address, _ = get_records("addresses", user_id)
                            except Exception:
                                default_address = None
                            
                            request.session['is_default_address'] = False
                            if default_address:
                                request.session['is_default_address'] = True

                            return redirect(reverse('djapp:dashboard'))
                except:
                    pass
            else:
                message = "Something wrong happend please try again. If you face any problem with signing up please contact us at support@"+domain+".com"
        except Exception as e:
                print(f"An error occurred: {e}")
                message = "Something wrong happend please try again. If you face any problem with signing up please contact us at support@"+domain+".com"
    return render(request, 'accounts/signup_2.html', locals())


def logout(request):
    del request.session['user_auth']
    return redirect(reverse("djapp:login"))


################################################################
# Custom Error Views
################################################################


def custom_500_view(request):
    return render(request, '500.html', {}, status=500)


def maintenance_view(request):
    return render(request, 'maintenance_page.html')


def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)


################################################################
# Dashboard Views
################################################################


@login_redirect
def dashboard(request):
    #print(blog_info["blogs"])
    context = {
        "page": "Dashboard",
        "page_name": "Dashboard",
        "blogs": blog_info["blogs"]
    }
    return render(request, 'v1/dashboard.html', context)


@login_redirect
def order_history(request):
    
    data = True
    try:
        history = get_history(request.session['user_auth'], request.session['time_difference'])
        history = history.tolist()
    except Exception:
        data = False
    
    if not history or (len(history) == 1 and history[0] == 1):
        data = False
    
    context = {
        "page": "Order History",
        "page_name": "Order History",
        "locals": locals(),
        "history": history,
        "data": data
    }
    return render(request, 'v1/services/order_history.html', context)


@login_redirect
def billing_history(request):
    
    data = True

    try:
        history = get_billing_history(request.session['user_auth'], request.session['time_difference'])
        history = history.tolist()
    except Exception:
        data = False
    
    if not history or (len(history) == 1 and history[0] == 1):
        data = False

    context = {
        "page": "Billing History",
        "page_name": "Billing History",
        "locals": locals(),
        "history": history,
        "data": data
    }
    return render(request, 'v1/services/billing_history.html', context)


@login_redirect
def guide(request):
    context = {
        "page": "Step-by-Step Guide",
        "page_name": "guide",
    }
    return render(request, 'v1/website/guide.html', context)


@login_redirect
def faq(request):
    get_faqs = get_FAQs()
    context = {
        "page": "Frequently Asked Questions",
        "page_name": "Frequently Asked Questions",
        'questions': get_faqs
    }
    return render(request, 'v1/website/faq.html', context)


@login_redirect
def term_and_condition(request):
    context = {
        "page": "Terms and Conditions",
        "page_name": "Terms and Condition",
    }
    return render(request, 'v1/website/terms.html', context)


@login_redirect
def pricing(request):
    context = {
        "page": "Pricing",
        "page_name": "Pricing",
    }
    return render(request, 'v1/services/pricing.html', context)


@login_redirect
def add_balance(request):
    wallet_address = get_user_wallet(request.session['user_auth'])
    context = {
        "page": "Add Balance",
        "page_name": "Add Balance",
        'walletadd': wallet_address
    }
    return render(request, 'v1/services/add_credit.html', context)


@login_redirect
def contact_us(request):
    context = {
        "page": "Contact Us",
        "page_name": "Contact Us",
    }

    if request.method == "POST":
        name = request.session['name']
        subject = request.POST['subject']
        email = request.session['email']
        desc = request.POST['desc']
        contactus(email, name, subject, desc)
        return JsonResponse(data={})

    return render(request, 'v1/website/contact.html', context)


@login_redirect
def blank_view(request):
    message = False
    if request.method == "POST":
        post_timestamp(request.session.get('user_auth'))
        message = "Clicked"
    return render(request, 'blank.html', locals())


@login_redirect
def invoice_view(request):
    get_session = request.session.get('invoice_details')

    if not get_session:
        return redirect(reverse('djapp:dashboard'))
    details = json.loads(get_session)

    if not isinstance(details[0][0], list):
        details = [[details[0]], details[1]]

    if request.method == "POST":
        get_value = send_request(request.session['user_auth'], details[1])
        return render(request, 'success-order.html', {'status': get_value[0], 'message': get_value[1]})

    return render(request, 'invoice.html', locals())



################################################################
# Single Label
################################################################


@csrf_exempt
def process_single_label(request):
    """
    Validates single label data submitted by the user.
    """

    data = {}
    result = []
    status = False

    head1 = ['FROM', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'TO',
             'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14',
             'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22']

    row1 = ['First name', 'Last name', 'Address', 'Address2', 'City', 'ZIP/Postal code', 'Abbreviation', 'First name',
            'Last name', 'Address', 'Address2', 'City', 'ZIP/Postal code', 'Abbreviation', 'weight', 'Ounces',
            'Length', 'width', 'Height', 'phone num1', 'phone num2', 'order num', 'Item-sku']

    row2 = [request.POST.get("firstname_2"), request.POST.get("lastname_2"),
            request.POST.get("address_2"), request.POST.get("address2_2"),
            request.POST.get("city_2"), request.POST.get("zip_code_2"),
            request.POST.get("abbreviation_2"), request.POST.get("firstname"),
            request.POST.get("lastname"), request.POST.get("address"),
            request.POST.get("address2"), request.POST.get("city"),
            request.POST.get("zip_code"), request.POST.get("abbreviation"),
            request.POST.get("weight"), request.POST.get("OuncesIN"),
            request.POST.get("LengthIN"), request.POST.get("WidthIN"),
            request.POST.get("HightIN"),
            request.POST.get("phone"),
            request.POST.get("phone_2"), request.POST.get("order_number"), request.POST.get("item_id")]
    
    new_address = [
        request.POST.get('firstname_2'),
        request.POST.get('lastname_2', ''),
        request.POST.get('address_2'),
        request.POST.get('address2_2', ''),
        request.POST.get('city_2'),
        request.POST.get('abbreviation_2'),
        request.POST.get('zip_code_2'),
        request.POST.get('phone_2', ''),
    ]

    new_package = [
        request.POST.get('package_name'),
        request.POST.get('LengthIN', ''),
        request.POST.get('WidthIN'),
        request.POST.get('HightIN', ''),
        request.POST.get('weight'),
        request.POST.get('OuncesIN'),
        request.POST.get("item_id")
    ]

    result, single_label_data = sl(pandas.DataFrame([row1, row2], columns=head1), request.session['user_auth'])

    
    if result == "error":
        status = True
        result = single_label_data
        single_data = False
    else:
        data['services'], data['sizes'] = load_services_with_prices_single_label(request.session['user_auth'], single_label_data)
        single_data = single_label_data
        status = False
    
    data['detail'] = 'Successful'
    data['response'] = result
    data['status'] = status
    data['new_package'] = new_package
    data['new_address'] = new_address
    data['single_data'] = single_data
    return JsonResponse(data, status=200)


@login_redirect
def single_label(request):
    """
    Single Label View page and continue modal post request.
    """
    
    default_address, saved_addresses = get_records('addresses', request.session['user_auth'])
    saved_packages = get_records('packages', request.session['user_auth'])

    if request.method == "POST":
        selected_size = request.POST.get('size')
        selected_service = request.POST.get('service')
        save_package = request.POST.get('save_package')
        save_address = request.POST.get('save_address')
        new_package = json.loads(request.POST.get('new_package'))
        new_address = json.loads(request.POST.get('new_address'))
        single_data = request.POST.get('single_data')

        if save_address:
            if save_address == "add_to_list":
                add_record('addresses', request.session['user_auth'], new_address)
            elif save_address == "add_as_default":
                returned_key = add_record('addresses', request.session['user_auth'], new_address)
                make_address_as_default(request.session['user_auth'], returned_key)

        if save_package == "1":
            add_record('packages', request.session['user_auth'], new_package)

        rate = request.POST.get('rate')
        data = single_data

        status, message = send_request_for_single_label(request.session['user_auth'], data, selected_service, selected_size, rate)
        return JsonResponse(data={'status': status, 'message': message})

    context = {
        "page": "Create a Single Label",
        "page_name": "Single Label",
        "default_address": default_address,
        "addresses": saved_addresses,
        "packages": saved_packages,
        "locals": locals()
    }
    return render(request, 'v1/services/single_label.html', context)


################################################################
# FORGET PASSWORD SECTION
################################################################


@csrf_exempt
def forgotpassword_views(request):
    message = False
    try:
        if request.method == "POST":
            emai = request.POST['email']
            email_exist, client_pass, userid = check_email_exists(emai)
            request.session['Verification-code'] = str(''.join(random.choices('0123456789', k=8))) #generate a code to send it to customer's email
            
            if not email_exist:
                message = "The email address you've entered is not registered with us."
            else:
                request.session['email_forget_pass'] = emai
                request.session['client_pass_forget_pass'] = client_pass
                request.session['userid_forget_pass'] = userid
                # send email with verification code to customer
                send_verification_code_email(emai, domain, request.session['Verification-code'])
                return redirect(reverse('djapp:verifypassword'))
    except Exception:
        message = "Something went wrong. Please contact us support@"+domain+".com"

    return render(request, 'accounts/forgotpassword.html', locals())


@csrf_exempt
@require_forgotpassword_access
def verifypassword_views(request):
    try:
        if request.method == "POST":
            ver_code = request.POST['vcode']
            newpass = request.POST['newpass']
            email = request.session['email_forget_pass']
        
            if ver_code == request.session['Verification-code']:
                try:
                    # Send an email to Customer and yourself and update database
                    password_reset_successful(email, newpass, domain)
                    message = "Your password has been successfully updated."
                    return redirect(reverse('djapp:login'))
                except Exception:
                    message = "Something went wrong. Please contact us support@"+domain+".com"
            else:
                message = "The verification code you entered is incorrect. Please try again. "
    except Exception:
        message = "Something went wrong. Please contact us support@"+domain+".com"
    return render(request, 'accounts/verifypassword.html', locals())
