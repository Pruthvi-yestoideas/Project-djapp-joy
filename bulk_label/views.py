import json
from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
import pandas as pd
from djapp.plugins.Home_Page import file_processing, load_services_with_prices_bulk, send_request_for_bulk_label, volume_max, weight_max
from settings.views import address_validation, get_records
from djapp.auth_login import login_redirect

# Create your views here.


@login_redirect
def bulk_label(request):
    """
    Step 1 view
    Bulk Label View page.
    """

    default_address, saved_addresses = get_records('addresses', request.session['user_auth'])
    saved_packages = get_records('packages', request.session['user_auth'])
    
    context = {
        "page": "Upload Spreadsheet (Step 1 of 3)",
        "page_name": "bulk",
        "default_address": default_address,
        "saved_addresses": saved_addresses,
        "saved_packages": saved_packages,
    }
    return render(request, 'v1/services/bulk_label.html', context)


def file_upload(request):
    """
    Step 1 processing:
    Handles a POST request containing an uploaded file. The function reads the uploaded file,
    validates its format (supports CSV, XLSX, and XLS), and processes the data using the
    file_processing function.

    Parameters:
    - request: The HTTP request object containing the uploaded file in the POST request.

    Returns:
    - A JsonResponse containing details of the processing result, including success or error status,
      processed data (address_sheet), error messages (errors), and details_err if applicable.

    Note:
    - The file is expected to be in CSV, XLSX, or XLS format.
    - If the file format is invalid or the content does not match the expected template, an error
      response is returned.
    - The processing result is obtained by calling the file_processing function, and the details
      are included in the JsonResponse.
    """
    
    if request.method == "POST":
        
        file = request.FILES["file"]
        file_name = str(file.name).lower()
        extension = file_name.split(".")[-1]
        addresses_sheet = []
        detail = "success"

        try:
            if extension == "csv":
                numpy_array = np.asarray(pd.read_csv(file).fillna(''))[1:, :23]
            elif extension == "xlsx" or extension == "xls":
                numpy_array = np.asarray(pd.read_excel(file).fillna(''))[1:, :23]
            else:
                err = ["only csv, xlsx, xls files are accepted!"]
                return JsonResponse({'detail': "error1", 'errors': err}, status=200)
        except Exception as e:
            err = ["Uploaded file doesn't match our template or may be empty!"]
            return JsonResponse({'detail': "error1", 'errors': err}, status=200)

        if extension == "xlsx" or extension == "xls" or extension == "csv":
            err, details_err, addresses_sheet = file_processing(numpy_array, request.session['user_auth'], True)
            addresses_sheet = addresses_sheet if isinstance(addresses_sheet, list) else []

        if isinstance(err, list) and len(err) > 0 and len(details_err) == 0:
            detail = "error1" 

        return JsonResponse({'detail': detail, 'address_sheet': json.dumps(numpy_array.tolist()), 'errors': err, 'details_err': details_err}, status=200)


@login_redirect
def upload_data(request):
    """
    Step 2 processing:
    Handles a POST request with an address sheet, processes the data using file_processing,
    and returns a JsonResponse with the processing result, including services and sizes if successful.
    """

    if request.method == "POST":
        addresses_sheet = request.POST.get("address_sheet")
        address_sheet = [item for item in json.loads(addresses_sheet) if item != 0]
        numpy_array = np.asarray(address_sheet, dtype=object)
        err, details_err, addresses_sheet = file_processing(numpy_array, request.session['user_auth'], False)
        error = True
        services = []
        sizes = []

        if isinstance(err, list) and len(err)==0 and len(details_err)==0:
            services, sizes = load_services_with_prices_bulk(request.session['user_auth'], numpy_array)
            error = False
        
        data = {
            'detail': 'Successful',
            'address_sheet': json.dumps(addresses_sheet.tolist()),
            'status': err,
            'services': services,
            'sizes': sizes,
            'details_err': details_err,
            'error': error,
            'errors': err
        }
        return JsonResponse(data, status=200)


def send_bulk_label_request(request):
    """
    Step 3 Processing:
    Handles a POST request for sending a bulk label request, extracting address sheet,
    services, size, and total sum. Sends the request using send_request_for_bulk_label
    and returns a JsonResponse with the processing status and message.
    """

    if request.method == "POST":
        addresses_sheet = request.POST.get("address_sheet")
        address_sheet = [item for item in json.loads(addresses_sheet) if item != 0]
        numpy_array = np.asarray(address_sheet, dtype=object)
        
        services = request.POST.get("services")
        services = json.loads(services)
        
        size = request.POST.get("size")
        total_sum = request.POST.get("total_sum")
        
        title, message = send_request_for_bulk_label(request.session['user_auth'], numpy_array, services, size, total_sum)
        
        return JsonResponse(data={"status": title, "message":message})


@login_redirect
def validate_address(request):

    if request.method == "POST":
        add_1 = request.POST.get('address1')
        add_2 = request.POST.get('address2', '')
        state = request.POST.get('state')
        city = request.POST.get('city')
        postal_code = request.POST.get('zip')
        response = address_validation(add_1, add_2, city, state, postal_code)

        if isinstance(response, list):
            return JsonResponse(data={'error': False, 'data': response})

    return JsonResponse(data={'error': True})


@login_redirect
def validate_package(request):

    if request.method == "POST":
        errors = []
        l = float(request.POST.get('length'))
        w = float(request.POST.get('width'))
        h = float(request.POST.get('height'))
        pounds = float(request.POST.get('pounds'))
        ounces = float(request.POST.get('ounces'))
        item_id = request.POST.get('item_id')
        
        if len(item_id) > 22:
            errors.append("Item id can not be more than 22 numbers")
        
        if pounds > weight_max:
            errors.append("Weight can not be more than " + str(weight_max))
        
        if ounces > 16:
            errors.append("Ounces can not be more than 16")

        if pounds + ounces <= 0:
            errors.append("Weight can not be less than or equal to 0!")
            
        if l*w*h > volume_max:
            errors.append("We don't offer labels with those Dimensions")
        
        if l*w*h == 0:
            errors.append("Dimension is invalid")
            

        return JsonResponse(data={'errors': errors})
        
        