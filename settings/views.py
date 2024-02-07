
'''
**so this functions will be used in the backend to edit in database and retrive from it as well
- the "record_type" variable is "addresses" or "packages"
- "user_ID" is already passed in the session when the user logged in
-if any of those functions returned false then please handle it properly in the front end
- you can get the records of both "addresses" or "packages" using the "get_records" function
for addresses it returns both all saved addresses and the current default address
but for packages there's no such a thing called default
- a client can add a new address or package through the "add_record" function
- a client can edit an address or package  through the "edit_record" function
Note (every address or package has its unique id which can be retrived from the "get_records" function')
- a client can delete an address or package  through the "delete_record" function
but a defualt address can't be deleted unless he choose to replace it with other one
using this function "make_address_address_as_default()"


record_type = "addresses" or "packages"
addrees = ["First Name", "Last Name", "address1", "address2", "City", "Zip Code", "State", "phone"]
package = ['name','length','width','Hight','lbs','oz']

'''


from django.shortcuts import redirect, render
from djapp.auth_login import login_redirect
from settings.config import firebase_config
import json
import requests
import pyrebase
import ast
from django.http import JsonResponse
from usps import USPSApi, Address
from djapp.plugins.domain_val import usps_key

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

usps = USPSApi(usps_key, test=True)
#USPS FUNCTIONS
def validate_address_without_ADD2(add_1, city0, stat, postal_code):
    address = Address(
        name='Tobin Brown',
        address_1=add_1,
        city=city0,
        state=stat,
        zipcode=postal_code
    )
    validation = usps.validate_address(address)
    return validation

def validate_address_with_ADD2(add_1, add_2, city0, stat, postal_code):
    address = Address(
        name='Tobin Brown',
        address_1=add_1,
        address_2=add_2,
        city=city0,
        state=stat,
        zipcode=postal_code
    )
    validation = usps.validate_address(address)
    return validation

#another api's functions
def ship_engin_validation(add_1, add_2, city0, stat, postal_code):
    url = "https://api.shipengine.com/v1/addresses/validate"
    headers = {
        "API-Key": 'v84wXVjBrhPOwr9dFUvwOSz+JKBxvpJ2CJiV5r6aR+k',
        "Content-Type": "application/json"
    }
    data = {
        "address_line1": add_1,
        "address_line2": add_2,
        "city_locality": city0,
        "state_province": stat,
        "postal_code": str(postal_code),
        "country_code": "US"
        }
    data = json.dumps([data])
    response = requests.post(url, headers=headers, data=data).json()[0]
    
    return response


#Main Validation function
def address_validation(add_1, add_2, city0, stat, postal_code):
    api_fail = False
    add_1 = add_1.strip()
    add_2 = add_2.upper()
    city0 = city0.strip()
    stat = stat.strip()
    postal_code = str(postal_code).split("-")[0]
    try:
        r = validate_address_without_ADD2(add_1, city0, stat, postal_code).result
        add2 = r['AddressValidateResponse']['Address']['Address1']
        add1 = r['AddressValidateResponse']['Address']['Address2']
        if add2 == '-': add2 = add_2
        cit = r['AddressValidateResponse']['Address']['City']
        abbri = r['AddressValidateResponse']['Address']['State']
        zip5 = r['AddressValidateResponse']['Address']['Zip5']
        zip4 = r['AddressValidateResponse']['Address']['Zip4']
        if zip4 != None:
            if len(zip4) > 2: zip5 = zip5 + "-" + zip4
        add_1 = add1
        add2 = add2
        city0 = cit
        stat = abbri
        postal_code = zip5
    except:
        # Try to add address2 if (failed) or (addrss 1 is placed in add2 and add2 is empty)
        try:
            r = validate_address_with_ADD2(add_1, add_2, city0, stat, postal_code).result
            try: add2 = r['AddressValidateResponse']['Address']['Address1']
            except: add2 = add_2
            add1 = r['AddressValidateResponse']['Address']['Address2']
            cit = r['AddressValidateResponse']['Address']['City']
            abbri = r['AddressValidateResponse']['Address']['State']
            zip5 = r['AddressValidateResponse']['Address']['Zip5']
            zip4 = r['AddressValidateResponse']['Address']['Zip4']
            if zip4 != None:
                if len(zip4) > 2: zip5 = zip5 + "-" + zip4
            add_1 = add1
            add_2 = add2
            city0 = cit
            stat = abbri
            postal_code = zip5
        except:
            #check if the error is address incorrect or is it limiting requests
            try:
                res_describ = r['AddressValidateResponse']['Address']['Error']['Description']
                if res_describ == 'Address Not Found.' or res_describ == 'Invalid State Code.' or res_describ == 'Invalid City.' or res_describ == "Invalid Zip Code.":
                    return "Return Address isn't Valid"
            except:
                api_fail = True
                print('free api failed')
                
    #alternative api's section
    try:         
        if api_fail == True:
            res = ship_engin_validation(add_1, add_2, city0, stat, postal_code)
            if res['status'] == 'verified':
                add_1 = res['matched_address']['address_line1']
                add_2 = res['matched_address']['address_line2']
                add_2 = '' if add_2 is None else add_2
                city0 = res['matched_address']['city_locality']
                stat = res['matched_address']['state_province']
                postal_code = res['matched_address']['postal_code'] 
            else:
                return "Return Address isn't Valid"
    except:
        return "Return Address isn't Valid"
    
    return [add_1, add_2, city0, stat, postal_code]


def add_record(record_type: str, user_ID: str, record: list):
    try:
        key = db.generate_key()
        db.child("user_settings").child(user_ID).child(record_type).update(
            {key: str(record)})
        return key
    except Exception:
        return False


def get_records(record_type: str, user_ID: str):
    try:
        data = json.loads(json.dumps(dict(db.child("user_settings").child(user_ID).child(record_type).get().val())))
        for key, value in data.items():
            data[key] = ast.literal_eval(value)

        if record_type == "addresses":
            all_records = {key: value for key, value in data.items() if key != "default"}
            default_record = None
            if "default" in data:
                default_record = data['default']

            return default_record, all_records
        elif record_type == "packages":
            return data

        return data
    except Exception as e:
        print(e)
        return {}


def edit_record(record_type: str, user_ID: str, record_ID: str, new_record: list):
    try:
        db.child("user_settings").child(user_ID).child(record_type).update(
            {record_ID: str(new_record)})
        return True
    except Exception as e:
        print(e)
        return False


def delete_record(record_type: str, user_ID: str, record_ID: str):
    try:
        db.child("user_settings").child(user_ID).child(record_type).child(record_ID).remove()
        return True
    except Exception:
        return False


def make_address_as_default_2(user_ID: str, address_ID_to_be_as_default: str):
    try:
        data = json.loads(json.dumps(dict(
            db.child("user_settings").child(user_ID).child("addresses").get().val())))[address_ID_to_be_as_default]
        db.child("user_settings").child(user_ID).child("addresses").update(
            {'default': data})
        db.child("user_settings").child(user_ID).child("addresses").child(address_ID_to_be_as_default).remove()
        return True
    except Exception:
        return False


def make_address_as_default(user_ID: str, address_ID_to_be_as_default: str):
    try:
        data0 = json.loads(json.dumps(dict(
            db.child("user_settings").child(user_ID).child("addresses").get().val())))
        data = data0[address_ID_to_be_as_default]
        previous_default = data0['default']
        db.child("user_settings").child(user_ID).child("addresses").update(
            {'default': data})
        db.child("user_settings").child(user_ID).child("addresses").update(
            {db.generate_key(): str(previous_default)})
        db.child("user_settings").child(user_ID).child("addresses").child(address_ID_to_be_as_default).remove()
        return True
    except Exception as e:
        print(e)
        return False


# on login if get_addresses() function returned false
def make_a_new_default_address(user_ID: str, address: list):
    try:
        db.child("user_settings").child(user_ID).child("addresses").update(
            {'default': str(address)})
        return True
    except Exception:
        return False


@login_redirect
def settings_view(request):
    context = {
        "page": "Settings",
        "main_page": "Settings"
    }
    return render(request, 'v1/settings/settings.html', context)


@login_redirect
def saved_packages(request):
    
    if request.method == "POST":
        package = [
            request.POST.get('name'),
            request.POST.get('length', ''),
            request.POST.get('width'),
            request.POST.get('height', ''),
            request.POST.get('pounds'),
            request.POST.get('ounces'),
            request.POST.get('item_id'),
        ]
        
        add_record('packages', request.session['user_auth'], package)
        return redirect('/settings/packages/')
    
    data = get_records('packages', request.session['user_auth'])
    context = {
        "page": "Saved Packages",
        "main_page": "Settings"
    }
    context['packages'] = data
    return render(request, 'v1/settings/saved_packages.html', context)


@login_redirect
def add_default_address(request):

    if request.method == "POST":
        add_1 = request.POST.get('address1')
        add_2 = request.POST.get('address2', '')
        state = request.POST.get('state')
        city = request.POST.get('city')
        postal_code = request.POST.get('zip')

        response = address_validation(add_1, add_2, city, state, postal_code)

        if isinstance(response, list):
            address = [
                request.POST.get('firstname'),
                request.POST.get('lastname', ''),
                response[0],
                response[1],
                response[2],
                response[3],
                response[4],
                request.POST.get('phone', ''),
            ]
            make_a_new_default_address(request.session['user_auth'], address)
            request.session['is_default_address'] = True
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': True})

    return redirect('/')


@login_redirect
def ship_from_addresses(request):

    if request.method == "POST":
        add_1 = request.POST.get('address1')
        add_2 = request.POST.get('address2', '')
        state = request.POST.get('state')
        city = request.POST.get('city')
        postal_code = request.POST.get('zip')
        save_as_default = request.POST.get('save_as_default')
        response = address_validation(add_1, add_2, city, state, postal_code)

        if isinstance(response, list):
            address = [
                request.POST.get('firstname'),
                request.POST.get('lastname', ''),
                response[0],
                response[1],
                response[2],
                response[3],
                response[4],
                request.POST.get('phone', ''),
            ]
            address_id = add_record('addresses', request.session['user_auth'], address)
            if save_as_default == "1":
                make_address_as_default(request.session["user_auth"], address_id)
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': response})

    default_record, all_records = get_records('addresses', request.session['user_auth'])
    context = {
        "page": "Ship From Addresses",
        "main_page": "Settings"
    }
    context['addresses'] = all_records
    context['default_record'] = default_record
    return render(request, 'v1/settings/saved_addresses.html', context)


def edit_package(request, record_id: str):
    if request.method == "POST":
        package = [
            request.POST.get('name'),
            request.POST.get('length'),
            request.POST.get('width'),
            request.POST.get('height'),
            request.POST.get('pounds'),
            request.POST.get('ounces'),
            request.POST.get('item_id'),
        ]
        edit_record("packages", request.session["user_auth"], record_id, package)
        
        return redirect('/settings/packages/')

    try:
        firebase = pyrebase.initialize_app(firebase_config)
        db = firebase.database()
        data = dict(db.child("user_settings").child(request.session["user_auth"]).child("packages").get().val())[record_id]
        data = {"package": ast.literal_eval(data)}
        return JsonResponse(data)
    except Exception as e:
        print(e)
        return JsonResponse({})


def edit_address(request, record_id: str):
    
    if request.method == "POST":
        add_1 = request.POST.get('address1')
        add_2 = request.POST.get('address2', '')
        state = request.POST.get('state')
        city = request.POST.get('city')
        postal_code = request.POST.get('zip')
        save_as_default = request.POST.get('save_as_default')

        response = address_validation(add_1, add_2, city, state, postal_code)
        print(response)
        if isinstance(response, list):
            address = [
                request.POST.get('firstname'),
                request.POST.get('lastname', ''),
                response[0],
                response[1],
                response[2],
                response[3],
                response[4],
                request.POST.get('phone', ''),
            ]
            edit_record("addresses", request.session["user_auth"], record_id, address)
            if save_as_default == "1":
                make_address_as_default(request.session["user_auth"], record_id)
            return JsonResponse({'error': False})
        else:
            return JsonResponse({'error': response})

    try:
        firebase = pyrebase.initialize_app(firebase_config)
        db = firebase.database()
        data = dict(db.child("user_settings").child(request.session["user_auth"]).child("addresses").get().val())[record_id]
        data = {"address": ast.literal_eval(data)}
        return JsonResponse(data)
    except Exception as e:
        print(e)
        return JsonResponse({})


def delete_address(request, record_id):

    delete_record('addresses', request.session['user_auth'], record_id)
        
    return JsonResponse({})


def delete_package(request, record_id):

    delete_record('packages', request.session['user_auth'], record_id)
        
    return JsonResponse({})
