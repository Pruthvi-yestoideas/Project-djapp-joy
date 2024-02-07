import numpy as np
import pandas as pd
import pyrebase
from datetime import datetime
np.set_printoptions(threshold=np.inf)
import ast
import numpy as np
import json
from usps import USPSApi, Address
from djapp.plugins.domain_val import domain_val
from djapp.plugins.config import config0,config1
from settings.views import usps, address_validation
import threading

domain = domain_val()
weight_max = 70
volume_max = 13000
columns_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                    'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC',
                    'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN']
state_arr = np.asarray(
    [['Alabama', 'AL'], ['Alaska', 'AK'], ['Arizona', 'AZ'], ['Arkansas', 'AR'], ['California', 'CA'],
        ['Colorado', 'CO'], ['Connecticut', 'CT'], ['Delaware', 'DE'], ['Florida', 'FL'], ['Georgia', 'GA'],
        ['Hawaii', 'HI'], ['Idaho', 'ID'], ['Illinois', 'IL'], ['Indiana', 'IN'], ['Iowa', 'IA'], ['Kansas', 'KS'],
        ['Kentucky', 'KY'], ['Louisiana', 'LA'], ['Maine', 'ME'], ['Maryland', 'MD'], ['Massachusetts', 'MA'],
        ['Michigan', 'MI'], ['Minnesota', 'MN'], ['Mississippi', 'MS'], ['Missouri', 'MO'], ['Montana', 'MT'],
        ['Nebraska', 'NE'], ['Nevada', 'NV'], ['New Hampshire', 'NH'], ['New Jersey', 'NJ'], ['New Mexico', 'NM'],
        ['New York', 'NY'], ['North Carolina', 'NC'], ['North Dakota', 'ND'], ['Ohio', 'OH'], ['Oklahoma', 'OK'],
        ['Oregon', 'OR'], ['Pennsylvania', 'PA'], ['Rhode Island', 'RI'], ['South Carolina', 'SC'],
        ['South Dakota', 'SD'], ['Tennessee', 'TN'], ['Texas', 'TX'], ['Utah', 'UT'], ['Vermont', 'VT'],
        ['Virginia', 'VA'], ['Washington', 'WA'], ['West Virginia', 'WV'], ['Wisconsin', 'WI'], ['Wyoming', 'WY'],
        ['District of Columbia', 'DC'], ['Marshall Islands', 'MH'], ['PUERTO RICO', 'PR']])

def is_nan(x):
    return (x is np.nan or x != x)


#############################################BULK UPLOAD##########################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################

# This Function takes a pandas dataframe of the inserted csv file and the user_id who uploaded the file
# then the function makes processing of file data
# and returns either the errors found in the file or succesful

#sub-function that does the initial analysis over the data
def initial_processing(addresses_sheet, user_ID):
    err = []
    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    flag_check = db.child("USERS").child(user_ID).child("flag").get().val()
    if (flag_check == 1):
        err.append('Try again later after we finish your previous request')
    if (len(addresses_sheet) <= 0):
        err.append('The Uploaded Sheet Is Empty')
    elif (len(addresses_sheet) > 100):
        err.append('The uploaded sheet exceeds the limit of 100 labels.')
    else:
        if (len(addresses_sheet[0])> 23):
            err.append('The uploaded sheet exceeds the number of columns specified in the template.')
        if (len(addresses_sheet[0])< 23):
            err.append('The uploaded sheet contains fewer columns than required by the template.')

    return err

#sub-function to analyize a chunk of numpy array from the uploaded file                        
def file_processing_partial(local_addresses_sheet, user_ID, verify_add, start_idx, end_idx, results, err, details_err, lock):
    # Initialize local variables for this subset
    local_err = []
    local_details_err = []

    #Vaildate on address by API call  
    if verify_add:
        for i in range(start_idx, end_idx):
            try:
                ship_to_validation = address_validation(local_addresses_sheet[i, 9], local_addresses_sheet[i, 10], local_addresses_sheet[i, 11]
                                        , local_addresses_sheet[i, 13], local_addresses_sheet[i, 12])
                print(ship_to_validation)
                if ship_to_validation == "Return Address isn't Valid":
                    local_details_err.append([[i, 9], 'Invalid Shipping Address'])
                elif(len(ship_to_validation) == 5):
                    (local_addresses_sheet[i, 9], local_addresses_sheet[i, 10], local_addresses_sheet[i, 11]
                                        , local_addresses_sheet[i, 13], local_addresses_sheet[i, 12]) = ship_to_validation
            except:
                local_details_err.append([[i, 9], 'ERROR: 500 (Address Validation API Failed)'])
        
    
    try:
        for i in range(start_idx, end_idx):
            add = local_addresses_sheet[i, :]
            for j in range(local_addresses_sheet.shape[1]):
                # EMPTY FIELDS CHECK
                try:
                    np.where(np.asarray([0, 2, 4, 5, 6, 7, 9, 11, 12, 13, 16, 17, 18]) == j)[0][0]
                    if (is_nan(add[j]) == True or add[j]==''):
                        local_details_err.append([[i, j], 'Empty Field'])
                    if (bool(str(add[j]).strip()) == False):
                        local_addresses_sheet[i, j] = ''
                except:
                    try:
                        if (bool(str(add[j]).strip()) == False):
                            local_addresses_sheet[i, j] = ''
                    except:
                        pass

                # Check ON ZIP-CODE
                if (j == 5 or j == 12):
                    local_addresses_sheet[i, j] = str(local_addresses_sheet[i, j]).strip()
                    if (len(str(add[j])) > 10):
                        local_details_err.append([[i, j], 'Invalid ZIP Code'])
                    else:
                        try:
                            # check on zip code
                            if (bool(add[j].strip()) == True):
                                try:
                                    int(add[j].strip().split('-')[0])
                                    try:
                                        int(add[j].strip().split('-')[1])
                                    except:
                                        pass
                                    local_addresses_sheet[i, j] = add[j].strip()
                                except:
                                    local_details_err.append([[i, j], 'Invalid ZIP Code'])
                        except:
                            pass
                        
                # Check On State
                elif (j == 6 or j == 13):
                    try:
                        local_addresses_sheet[i, j] = str(local_addresses_sheet[i, j]).upper()
                        if (bool(add[j].strip()) == True):
                            local_addresses_sheet[i, j] = add[j].strip()
                            if (len(local_addresses_sheet[i, j]) != 2 and len(
                                    np.where(state_arr[:, 0] == local_addresses_sheet[i, j])[0]) == 0):
                                local_details_err.append([[i, j], 'Invalid State'])
                            elif (len(local_addresses_sheet[i, j]) == 2 and len(
                                    np.where(state_arr[:, 1] == local_addresses_sheet[i, j])[0]) == 0):
                                local_details_err.append([[i, j], 'Invalid State'])
                            elif (len(local_addresses_sheet[i, j]) != 2 and len(
                                    np.where(state_arr[:, 0] == local_addresses_sheet[i, j])[0]) > 0):
                                local_addresses_sheet[i, j] = state_arr[
                                    np.where(state_arr[:, 0] == local_addresses_sheet[i, j])[0][0], 1]
                        else:
                            local_details_err.append([[i, j], 'Invalid State'])
                    except:
                        pass

                # check on length of 1st address and 2nd address
                elif (j == 2 or j == 3 or j == 9 or j == 10):
                    if (str(add[j]) != 'nan'):
                        if (len(str(add[j])) > 32):
                            local_details_err.append([[i, j], 'Address is too long'])
                            # check on city length
                elif (j == 4 or j == 11):
                    if (len(add[j].strip()) > 24):
                        local_details_err.append([[i, j], 'Invalid City'])

        # Check On Weights
        for i in range(start_idx, end_idx):
            try:
                # Check if both cells are empty
                if not str(local_addresses_sheet[i, 14]).strip() and not str(local_addresses_sheet[i, 15]).strip():
                    local_details_err.append([[i, 14], "Weight Can't Be Empty"])
                    local_details_err.append([[i, 15], "Weight Can't Be Empty"])
                else:
                    try: local_addresses_sheet[i, 14] = float(str(local_addresses_sheet[i, 14]).strip())
                    except: local_addresses_sheet[i, 14] = 0.0
                    try: local_addresses_sheet[i, 15] = float(str(local_addresses_sheet[i, 15]).strip())
                    except: local_addresses_sheet[i, 15] = 0.0
                    total_weight = local_addresses_sheet[i, 14] + local_addresses_sheet[i, 15]/16
                    
                    if (total_weight > weight_max):
                        local_details_err.append([[i, 14], "Weight Exceeded " + str(weight_max) + " lbs"])
                        local_details_err.append([[i, 15], "Weight Exceeded " + str(weight_max) + " lbs"])
                    if (total_weight <= 0):
                        local_details_err.append([[i, 15], "Weight Can't Be Less Than 0 oz"])
            except:
                local_details_err.append([[i, 14], "Invalid Weight"])
                local_details_err.append([[i, 15], "Invalid Weight"])

        #check on the Volume
        for i in range(start_idx, end_idx):
            try:
                local_addresses_sheet[i, 16] = float(str(local_addresses_sheet[i, 16]).strip())
                local_addresses_sheet[i, 17] = float(str(local_addresses_sheet[i, 17]).strip())
                local_addresses_sheet[i, 18] = float(str(local_addresses_sheet[i, 18]).strip())
                total_volume = local_addresses_sheet[i, 16] * local_addresses_sheet[i, 17] * local_addresses_sheet[i, 18]
                if total_volume > volume_max:
                    local_details_err.append([[i, 16], "Maximum dimensions must not exceed " + str(volume_max) + " cubic inches."])
                elif total_volume == 0:
                    local_details_err.append([[i, 16], "Dimensions Is Not Valid"])
            except:
                local_details_err.append([[i, 16], "Dimensions Is Not Defined"])


        # check on first and last name length
        for i in range(start_idx, end_idx):
            try:
                if ((len(local_addresses_sheet[i, 0]) + len(local_addresses_sheet[i, 1]) + 1) > 32):
                    local_details_err.append([[i, 0], 'Return Name Is Too Long'])
                    local_details_err.append([[i, 1], 'Return Name Is Too Long'])
            except:
                if ((len(local_addresses_sheet[i, 0]) + 1) > 32):
                    local_details_err.append([[i, 0], 'Return Name Is Too Long'])
            try:
                if ((len(local_addresses_sheet[i, 7]) + len(local_addresses_sheet[i, 8]) + 1) > 32):
                    local_details_err.append([[i, 7], 'Shipping Name Is Too Long'])
                    local_details_err.append([[i, 8], 'Shipping Name Is Too Long'])
            except:
                if ((len(local_addresses_sheet[i, 7]) + 1) > 32):
                    local_details_err.append([[i, 7], 'Shipping Name Is Too Long'])

    except Exception as e:
        print("An error occurred:", e)
        local_err.append("ERROR: 200")


    # Use lock to safely update shared lists
    with lock:
        # Update the main array with processed data
        #addresses_sheet[start_idx:end_idx] = local_addresses_sheet
        err.append(local_err)
        details_err.append(local_details_err)
        results[start_idx:end_idx] = local_addresses_sheet[start_idx:end_idx]

#sub-function that do the multi-threading
def file_processing_threads(addresses_sheet, user_ID, verify_add, num_threads=1):
    one_thread_handles = 6
    n = len(addresses_sheet)
    num_threads = int(n/one_thread_handles + 0.99999999999999)
    chunk_size = (n + num_threads - 1) // num_threads  # Ceiling division
    threads = []
    results = np.empty_like(addresses_sheet)
    err = []
    details_err = []
    lock = threading.Lock()

    for i in range(num_threads):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, n)

        t = threading.Thread(target=file_processing_partial, args=(
            addresses_sheet, user_ID, verify_add, start_idx, end_idx, results, err, details_err, lock))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Combine the results, err, and details_err from all threads
    # Ensure they are in the correct order
    final_results = results
    final_err = []
    final_details_err = []
    
    for e in err:
        if e is not None:
            final_err.extend(e)
    final_err = list(dict.fromkeys(final_err))
    for de in details_err:
        if de is not None:
            final_details_err.extend(de)
    final_details_err = sorted(final_details_err, key=lambda x: (x[0][0], x[0][1]))
    
    
    if (len(final_err) == 0 and len(final_details_err) == 0):
        try:
            firebase = pyrebase.initialize_app(config0)
            db = firebase.database()
            db.child("USERS").child(user_ID).update(
                {"data": np.array2string(addresses_sheet, separator=',').replace('\n', '')})
            return final_err, final_details_err, final_results
        except:
            final_err.append("ERROR: 250")

    return final_err, final_details_err, final_results


#The main function to be called
def file_processing(addresses_sheet, user_ID, verify_add):
    ''' the addresses_sheet is a numpy array and should be passed like this
        addresses_sheet = np.asarray(pandas_dataframe.fillna(''))[1:, :23]
    '''
    details_err = []
    red_err = initial_processing(addresses_sheet, user_ID)
    if len(red_err)>0:
        return red_err, details_err, None
    #now the below is in case that the file passes the initial processing then:
    #make the multithread from here
    try:
        err, details_err, addresses_sheet = file_processing_threads(addresses_sheet, user_ID, verify_add)
        red_err.extend(err)
    except:
        red_err.append("An error has occurred. Please ensure that you are using our template correctly.")
    return red_err, details_err, addresses_sheet 
    

# This function takes the bulk_data retured from thr file_processing function
def load_services_with_prices_bulk(user_ID, bulk_data):
    """
    gets services and sizes availible for the given user and its submitted data.
    """

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()
    
    all_services = db.child("all_services").get().val().split(',')
    sizes = db.child("all_sizes").get().val().split(',')
    
    for service in all_services:
        if service == 'Ground Advantage':
            ground_rate = float(db1.child(user_ID).child(service).get().val())
        else:
            priority_rates = db1.child(user_ID).child(service).get()
            keys = []
            p_values = []
            for item in priority_rates.each():
                keys.append(item.key())
                p_values.append(item.val())
            keys = [int(key) for key in keys]
            keys.sort()
            p_values.sort()


    lst_of_all_label_services = []

    for i in range(len(bulk_data)):
        
        weight_lbs = float(bulk_data[i][14])
        weight_oz = float(bulk_data[i][15])
        total_weight = weight_lbs + weight_oz/16
        
        services = all_services
        if total_weight > 0.9994:
            # exclude ground label from services if weight exceeds 1 lbs
            services = [service for service in services if service != 'Ground Advantage']
        
        lst_of_services = []
        for service in services:
            if service == 'Ground Advantage':
                rate = ground_rate
            else:
                for k in range(len(keys)):
                    if (int(float(total_weight)) <= keys[k]):
                        rate = p_values[k]
                        break
            service_dic = {
                'name': service,
                'rate': rate
            }
            lst_of_services.append(service_dic) #combines the allowed service for each label

        #make all the 2-demensional tabel of services
        lst_of_all_label_services.append(lst_of_services)     
    return lst_of_all_label_services, sizes


#last step after the user selects the service and sizes 
def send_request_for_bulk_label(user_ID, bulk_data, selected_service, selected_size, total_sum):

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()

    bal_val = db1.child(user_ID).child("balance").get().val()
    if (bal_val >= float(total_sum)):
        title = "Success!"
        message = "Your request has been successfully processed. You will shortly receive an email with your shipping labels, or you may review your order history shortly. Thank you."
        data2lst = bulk_data.tolist()
        selected_size = [selected_size] * len(selected_service)
        for i, row in enumerate(data2lst):
            row.append(selected_service[i])
            row.append(selected_size[i])
        
        if (len(data2lst[0]) == 25):
            db.child("RequestsPool").child(user_ID).child(db.generate_key()).update(
                {
                    "data": np.array2string(np.array(data2lst), separator=',').replace('\n', '')
                })
        else:
            title = "Oops!"
            message = "Order processing failed: Incomplete data provided."
    else:
        title = "Oops!"
        message = "Your current wallet balance is insufficient to process this request. Please top-up your wallet to continue. Thank you."
    return title, message



############################################Single Label###########################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################


def single_label(pandas_dataframe, user_ID):
    
    err = []

    try:
        addresses_sheet = np.asarray(pandas_dataframe.fillna(''))[1:, :23]
        firebase = pyrebase.initialize_app(config0)
        db = firebase.database()
        if (len(addresses_sheet) <= 0):
            err.append('The Uploaded Sheet Is Empty')

        for i in range(len(addresses_sheet)):
            add = addresses_sheet[i, :]
            for j in range(addresses_sheet.shape[1]):
                # EMPTY FIELDS CHECK
                try:
                    np.where(np.asarray([0, 2, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18]) == j)[0][0]
                    if (is_nan(add[j]) == True):
                        err.append('Found Empty Field')
                    if (bool(str(add[j]).strip()) == False):
                        addresses_sheet[i, j] = ''
                except:
                    try:
                        if (bool(str(add[j]).strip()) == False):
                            addresses_sheet[i, j] = ''
                    except:
                        pass

                # Check ON ZIP-CODE
                if (j == 5 or j == 12):
                    addresses_sheet[i, j] = str(addresses_sheet[i, j]).strip()
                    if (len(str(add[j])) > 10):
                        err.append("ZIP Code Is Not Defined")
                    else:
                        try:
                            # check on zip code
                            if (bool(add[j].strip()) == True):
                                try:
                                    int(add[j].strip().split('-')[0])
                                    try:
                                        int(add[j].strip().split('-')[1])
                                    except:
                                        pass
                                    addresses_sheet[i, j] = add[j].strip()
                                except:
                                    err.append("ZIP Code Is Not Defined")
                        except:
                            pass

                # Check On State
                elif (j == 6 or j == 13):
                    try:
                        addresses_sheet[i, j] = str(addresses_sheet[i, j]).upper()
                        if (bool(add[j].strip()) == True):
                            addresses_sheet[i, j] = add[j].strip()
                            if (len(addresses_sheet[i, j]) != 2 and len(
                                    np.where(state_arr[:, 0] == addresses_sheet[i, j])[0]) == 0):
                                err.append("Label Can't Be Created")
                            elif (len(addresses_sheet[i, j]) == 2 and len(
                                    np.where(state_arr[:, 1] == addresses_sheet[i, j])[0]) == 0):
                                err.append("Label Can't Be Created")
                            elif (len(addresses_sheet[i, j]) != 2 and len(
                                    np.where(state_arr[:, 0] == addresses_sheet[i, j])[0]) > 0):
                                addresses_sheet[i, j] = state_arr[
                                    np.where(state_arr[:, 0] == addresses_sheet[i, j])[0][0], 1]
                        else:
                            err.append("Label Can't Be Created")
                    except:
                        pass

                # check on length of 1st address and 2nd address
                elif (j == 2 or j == 3 or j == 9 or j == 10):
                    if (str(add[j]) != 'nan'):
                        if (len(str(add[j])) > 32):
                            err.append("Too Long Address")
                            # check on city length
                elif (j == 4 or j == 11):
                    if (len(add[j].strip()) > 24):
                        err.append("City Not Defined")
        
        # Check On Weightslbs
        for i in range(len(addresses_sheet)):
            try:
                addresses_sheet[i, 14] = float(str(addresses_sheet[i, 14]).strip())
                addresses_sheet[i, 15] = float(str(addresses_sheet[i, 15]).strip())
                total_weight = addresses_sheet[i, 14] + addresses_sheet[i, 15]/16
                
                if (total_weight > weight_max):
                    err.append("Weight Exceeded " + str(weight_max) + " lbs")
                if (total_weight <= 0):
                    err.append("Weight Can't Be Less Than 0 oz")
            except:
                err.append("Weight Is Not Defined")
            print('weight='+str(addresses_sheet[i, 14]))
        
        #check on the Volume
        for i in range(len(addresses_sheet)):
            try:
                addresses_sheet[i, 16] = float(str(addresses_sheet[i, 16]).strip())
                addresses_sheet[i, 17] = float(str(addresses_sheet[i, 17]).strip())
                addresses_sheet[i, 18] = float(str(addresses_sheet[i, 18]).strip())
                total_volume = addresses_sheet[i, 16] * addresses_sheet[i, 17] * addresses_sheet[i, 18]
                if total_volume > volume_max:
                    err.append("Maximum dimensions must not exceed " + str(volume_max) + " cubic inches.")
            except:
                err.append("Dimensions Is Not Defined")

        # check on first and last name length
        for i in range(len(addresses_sheet)):
            try:
                if ((len(addresses_sheet[i, 0]) + len(addresses_sheet[i, 1]) + 1) > 32):
                    err.append("Return Name Is Too Long")
            except:
                if ((len(addresses_sheet[i, 0]) + 1) > 32):
                    err.append("Return Name Is Too Long")
            try:
                if ((len(addresses_sheet[i, 7]) + len(addresses_sheet[i, 8]) + 1) > 32):
                    err.append("Shipping Name Is Too Long")
            except:
                if ((len(addresses_sheet[i, 7]) + 1) > 32):
                    err.append("Shipping Name Is Too Long")

    except:
        err.append("ERROR: 200")
    # this try and excpet make the request magic for address validation

    try:
        for i in range(len(addresses_sheet)):
            ship_to_validation = address_validation(addresses_sheet[i, 9], addresses_sheet[i, 10], addresses_sheet[i, 11]
                                     , addresses_sheet[i, 13], addresses_sheet[i, 12])
            if ship_to_validation == "Return Address isn't Valid":
                err.append("Shipping Address isn't Valid")
            elif(len(ship_to_validation) == 5):
                (addresses_sheet[i, 9], addresses_sheet[i, 10], addresses_sheet[i, 11]
                                     , addresses_sheet[i, 13], addresses_sheet[i, 12]) = ship_to_validation

    except:
        err.append("ERROR: 500")

    if (len(err) == 0):
        try:
            # firebase = pyrebase.initialize_app(config0)
            # db = firebase.database()
            # db.child("USERS").child(user_ID).update(
            #     {"data": np.array2string(addresses_sheet, separator=',').replace('\n', '')})
            return "UPLOADED SUCCESSFULLY", np.array2string(addresses_sheet, separator=',').replace('\n', '')
        except:
            err.append("ERROR: 250")
    if (len(err) > 0):
        err
        return "error", err


def load_services_with_prices_single_label(user_ID, single_label_data):
    """
    gets services and sizes availible for the given user and its submitted data.
    """

    lst = []
    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()
    
    services = db.child("all_services").get().val().split(',')
    sizes = db.child("all_sizes").get().val().split(',')
    data = np.char.strip(np.asarray(ast.literal_eval(single_label_data.replace("/", '|'))))
    weight_lbs = float(data[0][14])
    weight_oz = float(data[0][15])
    total_weight = weight_lbs + weight_oz/16
    
    if total_weight > 0.9994:
        # exclude ground label from services
        services = [service for service in services if service != 'Ground Advantage']

    for service in services:
        if service == 'Ground Advantage':
            rate = float(db1.child(user_ID).child(service).get().val())
        else:
            keys = np.sort(np.int_(np.asarray(ast.literal_eval(
                str(db1.child(user_ID).child(service).shallow().get().val()).split("(")[1].split(")")[0]))))
            for k in range(len(keys)):
                if (int(float(total_weight)) <= keys[k]):
                    rate = db1.child(user_ID).child(service).child(str(keys[k])).get().val()
                    break

        service = {
            'name': service,
            'rate': rate
        }
        lst.append(service)
    return lst, sizes


def send_request_for_single_label(user_ID, data, selected_service, selected_size, total_sum):

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()

    bal_val = db1.child(user_ID).child("balance").get().val()
    if (bal_val >= float(total_sum)):
        title = "Success!"
        message = "Your request has been successfully processed. You will shortly receive an email with your shipping labels, or you may review your order history shortly. Thank you."
        data = np.char.strip(np.asarray(ast.literal_eval(data.replace("/", '|'))))
        data_lst = data.tolist()
        data_lst[0] += [selected_service, selected_size]
        
        if (len(data_lst[0]) == 25):
            db.child("RequestsPool").child(user_ID).child(db.generate_key()).update(
                {
                    "data": np.array2string(np.array(data_lst), separator=',').replace('\n', '')
                })
        else:
            title = "Oops!"
            message = "Order processing failed: Incomplete data provided."
    else:
        title = "Oops!"
        message = "Your current wallet balance is insufficient to process this request. Please top-up your wallet to continue. Thank you."
    return title, message




######################make invoice###################


def on_continue_pressed(user_ID, selected_service, selected_size):
    # take the service selected  and push it to database0

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    db.child("USERS").child(user_ID).update({'service_type': str(selected_service)})
    db.child("USERS").child(user_ID).update({'size': str(selected_size)})
    # Make Invoice

    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()
    # Make Invoice to flat rate or Not A flat Rate
    if (selected_service[0:9] == 'Flat Rate' or selected_service == "Ground Advantage"):
        no_of_labels_flat_rate = len(
            np.asarray(ast.literal_eval(db.child('USERS').child(user_ID).child('data').get().val()))[:, 0])
        rate = float(db1.child(user_ID).child(selected_service).get().val())
        total = rate * no_of_labels_flat_rate
        invoice = [str(no_of_labels_flat_rate) + 'x ' + '$' + str(rate) , str(selected_service), str(total)]
    else:
        invoice = []
        weights = np.asarray(ast.literal_eval(db.child('USERS').child(user_ID).child('data').get().val()))[:, 14]
        uniqueValues, occurCount = np.unique(weights, return_counts=True)

        keys = np.sort(np.int_(np.asarray(ast.literal_eval(
            str(db1.child(user_ID).child(selected_service).shallow().get().val()).split("(")[1].split(")")[0]))))
        for i in range(len(uniqueValues)):
            for k in range(len(keys)):
                if (int(float(uniqueValues[i])) <= keys[k]):
                    rate = db1.child(user_ID).child(selected_service).child(str(keys[k])).get().val()
                    total = rate * occurCount[i]
                    invoice.append([str(occurCount[i]) + 'x ' + '$' + str(rate) ,
                                    str(uniqueValues[i]) + 'lb ' + str(selected_service), str(total)])
                    break
    if (len(invoice) > 0):
        try:
            sum_of_total = np.sum(np.asarray(invoice)[:, -1].astype(float))
        except:
            sum_of_total = invoice[-1]
        return invoice, sum_of_total

# This function will be executed on the send request button in the last page
def send_request(user_ID, total_sum):

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()

    flag_val = db.child("USERS").child(user_ID).child("flag").get().val()
    if (flag_val == 1):
        title = "Oops!"
        message = "We can't process your request now. we currently processing your previous request, it could take up to 15 minutes"
    else:
        bal_val = db1.child(user_ID).child("balance").get().val()
        if (bal_val >= float(total_sum)):
            title = "Success!"
            message = "We have successfully received your request. You will receive an email containing your shipping labels shortly. Thanks"
            db.child("USERS").child(user_ID).update({'flag': 1})
        else:
            title = "Oops!"
            message = "Your current wallet balance is insufficient to process this request. Please top-up your wallet to continue. Thank you."
    return title, message

# This function to retreive all the services which will be displayed in the dropdown menu
def load_all_available_services():
    
    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    services = db.child("all_services").get().val().split(',')
    return services


# This function to retreive all the sizes which will be displayed in the dropdown menu
def load_all_available_sizes():

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    sizes = db.child("all_sizes").get().val().split(',')
    return sizes


############################################Getters###########################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################

# This function take the userID and it return the balace of the customer
def get_balance(user_ID):

    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()
    balance = db1.child(user_ID).child('balance').get().val()
    return "$" + "{:.2f}".format(round(balance, 2))

# This function is returning questions and answers in array
def get_FAQs():

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    l = []
    qa = json.loads(json.dumps(dict(db.child("FAQ").get().val())))
    q = list(qa)
    for i in range(len(q)):
        l.append([q[i], qa[q[i]]])
    return np.asarray(l)

def get_user_Name(user_ID):

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    return db.child("USERS").child(user_ID).child("email_name").get().val().split(",")[1]

def post_client_id(user_ID, client_ip):

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    db.child("USERS").child(user_ID).update({'client_ip': str(client_ip)})

def get_user_wallet(user_ID):

    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    return db.child("USERS").child(user_ID).child("wallet").get().val()

##################################################################################
##################################################################################
##################################################################################
##################################################################################
##################################################################################
##################################################################################

'''
def file_processing(addresses_sheet, user_ID):
    #the addresses_sheet is a numpy array and should be passed like this
    #addresses_sheet = np.asarray(pandas_dataframe.fillna(''))[1:, :23]
    
    err = []
    details_err = []

    try:
        firebase = pyrebase.initialize_app(config0)
        db = firebase.database()
        flag_check = db.child("USERS").child(user_ID).child("flag").get().val()
        if (flag_check == 1):
            err.append('Try again later after we finish your previous request')
            return err, details_err, None
        if (len(addresses_sheet) <= 0):
            err.append('The Uploaded Sheet Is Empty')
        if (len(addresses_sheet) > 100):
            err.append('The uploaded sheet exceeds the limit of 100 labels.')
            return err, details_err, None

        #Vaildate on address by API call        
        try:
            for i in range(len(addresses_sheet)):
                ship_to_validation = address_validation(addresses_sheet[i, 9], addresses_sheet[i, 10], addresses_sheet[i, 11]
                                        , addresses_sheet[i, 13], addresses_sheet[i, 12])
                if ship_to_validation == "Return Address isn't Valid":
                    details_err.append([[i, 9], 'Invalid Shipping Address'])
                elif(len(ship_to_validation) == 5):
                    (addresses_sheet[i, 9], addresses_sheet[i, 10], addresses_sheet[i, 11]
                                        , addresses_sheet[i, 13], addresses_sheet[i, 12]) = ship_to_validation
                    
        except:
            err.append("ERROR: 500 (Address Validation API Failed)")

        for i in range(len(addresses_sheet)):
            add = addresses_sheet[i, :]
            for j in range(addresses_sheet.shape[1]):
                # EMPTY FIELDS CHECK
                try:
                    np.where(np.asarray([0, 2, 4, 5, 6, 7, 9, 11, 12, 13, 16, 17, 18]) == j)[0][0]
                    if (is_nan(add[j]) == True or add[j]==''):
                        details_err.append([[i, j], 'Empty Field'])
                    if (bool(str(add[j]).strip()) == False):
                        addresses_sheet[i, j] = ''
                except:
                    try:
                        if (bool(str(add[j]).strip()) == False):
                            addresses_sheet[i, j] = ''
                    except:
                        pass

                # Check ON ZIP-CODE
                if (j == 5 or j == 12):
                    addresses_sheet[i, j] = str(addresses_sheet[i, j]).strip()
                    if (len(str(add[j])) > 10):
                        details_err.append([[i, j], 'Invalid ZIP Code'])
                    else:
                        try:
                            # check on zip code
                            if (bool(add[j].strip()) == True):
                                try:
                                    int(add[j].strip().split('-')[0])
                                    try:
                                        int(add[j].strip().split('-')[1])
                                    except:
                                        pass
                                    addresses_sheet[i, j] = add[j].strip()
                                except:
                                    details_err.append([[i, j], 'Invalid ZIP Code'])
                        except:
                            pass

                # Check On State
                elif (j == 6 or j == 13):
                    try:
                        addresses_sheet[i, j] = str(addresses_sheet[i, j]).upper()
                        if (bool(add[j].strip()) == True):
                            addresses_sheet[i, j] = add[j].strip()
                            if (len(addresses_sheet[i, j]) != 2 and len(
                                    np.where(state_arr[:, 0] == addresses_sheet[i, j])[0]) == 0):
                                details_err.append([[i, j], 'Invalid State'])
                            elif (len(addresses_sheet[i, j]) == 2 and len(
                                    np.where(state_arr[:, 1] == addresses_sheet[i, j])[0]) == 0):
                                details_err.append([[i, j], 'Invalid State'])
                            elif (len(addresses_sheet[i, j]) != 2 and len(
                                    np.where(state_arr[:, 0] == addresses_sheet[i, j])[0]) > 0):
                                addresses_sheet[i, j] = state_arr[
                                    np.where(state_arr[:, 0] == addresses_sheet[i, j])[0][0], 1]
                        else:
                            details_err.append([[i, j], 'Invalid State'])
                    except:
                        pass

                # check on length of 1st address and 2nd address
                elif (j == 2 or j == 3 or j == 9 or j == 10):
                    if (str(add[j]) != 'nan'):
                        if (len(str(add[j])) > 32):
                            details_err.append([[i, j], 'Address is too long'])
                            # check on city length
                elif (j == 4 or j == 11):
                    if (len(add[j].strip()) > 24):
                        details_err.append([[i, j], 'Invalid City'])

        # Check On Weights
        for i in range(len(addresses_sheet)):
            try:
                # Check if both cells are empty
                if not str(addresses_sheet[i, 14]).strip() and not str(addresses_sheet[i, 15]).strip():
                    details_err.append([[i, 14], "Weight Can't Be Empty"])
                    details_err.append([[i, 15], "Weight Can't Be Empty"])
                else:
                    try: addresses_sheet[i, 14] = float(str(addresses_sheet[i, 14]).strip())
                    except: addresses_sheet[i, 14] = 0.0
                    try: addresses_sheet[i, 15] = float(str(addresses_sheet[i, 15]).strip())
                    except: addresses_sheet[i, 15] = 0.0
                    total_weight = addresses_sheet[i, 14] + addresses_sheet[i, 15]/16
                    
                    if (total_weight > weight_max):
                        details_err.append([[i, 14], "Weight Exceeded " + str(weight_max) + " lbs"])
                        details_err.append([[i, 15], "Weight Exceeded " + str(weight_max) + " lbs"])
                    if (total_weight <= 0):
                        details_err.append([[i, 15], "Weight Can't Be Less Than 0 oz"])
            except:
                details_err.append([[i, 14], "Invalid Weight"])
                details_err.append([[i, 15], "Invalid Weight"])

        #check on the Volume
        for i in range(len(addresses_sheet)):
            try:
                addresses_sheet[i, 16] = float(str(addresses_sheet[i, 16]).strip())
                addresses_sheet[i, 17] = float(str(addresses_sheet[i, 17]).strip())
                addresses_sheet[i, 18] = float(str(addresses_sheet[i, 18]).strip())
                total_volume = addresses_sheet[i, 16] * addresses_sheet[i, 17] * addresses_sheet[i, 18]
                if total_volume > volume_max:
                    details_err.append([[i, 16], "We Don't offer labels with those Dimensions"])
                elif total_volume == 0:
                    details_err.append([[i, 16], "Dimensions Is Not Valid"])
            except:
                details_err.append([[i, 16], "Dimensions Is Not Defined"])


        # check on first and last name length
        for i in range(len(addresses_sheet)):
            try:
                if ((len(addresses_sheet[i, 0]) + len(addresses_sheet[i, 1]) + 1) > 32):
                    details_err.append([[i, 0], 'Return Name Is Too Long'])
                    details_err.append([[i, 1], 'Return Name Is Too Long'])
            except:
                if ((len(addresses_sheet[i, 0]) + 1) > 32):
                    details_err.append([[i, 0], 'Return Name Is Too Long'])
            try:
                if ((len(addresses_sheet[i, 7]) + len(addresses_sheet[i, 8]) + 1) > 32):
                    details_err.append([[i, 7], 'Shipping Name Is Too Long'])
                    details_err.append([[i, 8], 'Shipping Name Is Too Long'])
            except:
                if ((len(addresses_sheet[i, 7]) + 1) > 32):
                    details_err.append([[i, 7], 'Shipping Name Is Too Long'])

    except:
        err.append("ERROR: 200")
    # this try and excpet make the request magic for address validation

    if (len(err) == 0 and len(details_err) == 0):
        try:
            # firebase = pyrebase.initialize_app(config0)
            # db = firebase.database()
            # db.child("USERS").child(user_ID).update(
            #     {"data": np.array2string(addresses_sheet, separator=',').replace('\n', '')})
            return err, details_err, addresses_sheet
        except:
            err.append("ERROR: 250")
    
    return err, details_err, addresses_sheet
    
'''