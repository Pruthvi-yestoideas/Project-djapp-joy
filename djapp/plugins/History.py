
import numpy as np
import pandas as pd
import json
import pyrebase
from datetime import datetime, timedelta
from djapp.plugins.domain_val import domain_val
from djapp.plugins.config import config3

domain = domain_val()


def parse_date(date_str):
    for fmt in ("%m-%d-%Y %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    return pd.NaT  # Return NaT (Not a Time) if no format matches


#This Function retreive the history data for each user
def get_history(user_ID, time_diff_utc):

    firebase3 = pyrebase.initialize_app(config3)
    db3 = firebase3.database()
    ls = []
    try:
        hist = json.loads(json.dumps(dict(db3.child("USERS").child(user_ID).child("transactionHistory").get().val())))
        if hist:
            # Convert to dictionary if necessary
            if isinstance(hist, str):
                hist = json.loads(hist)
        
            # Create a DataFrame from the dictionary
            df = pd.DataFrame(list(hist.items()), columns=['TransactionID', 'Data'])
        
            # Split the 'Data' column into multiple columns
            df[['Col1', 'Col2', 'Col3', 'Col4', 'Col5']] = df['Data'].str.split(',', expand=True)
        
            # Drop the original 'Data' column
            df.drop('Data', axis=1, inplace=True)
        
            #offset the dates to user timezone
            try:
                #df['Col1'] = pd.to_datetime(df['Col1'], format="%m-%d-%Y %H:%M")
                df['Col1'] = df['Col1'].apply(parse_date)
                df['Col1'] = df['Col1'] - pd.to_timedelta(time_diff_utc, unit='h')
                df['Col1'] = df['Col1'].dt.strftime("%m-%d-%Y %H:%M")
            except:
                pass
            
            ls = df.values.tolist()
        else:
            ls.append(['','','','','',''])
    except:
        ls.append(['','','','','',''])
    return np.asarray(ls)



def get_billing_history(user_ID, time_diff_utc):
    firebase3 = pyrebase.initialize_app(config3)
    db3 = firebase3.database()
    ls = []

    try:
        hist = json.loads(json.dumps(dict(db3.child("USERS").child(user_ID).child("billingHistory").get().val())))
        if hist:
            # Convert to dictionary if necessary
            if isinstance(hist, str):
                hist = json.loads(hist)
        
            # Create a DataFrame from the dictionary
            df = pd.DataFrame(list(hist.items()), columns=['TransactionID', 'Data'])
        
            # Split the 'Data' column into multiple columns
            df[['Col1', 'Col2']] = df['Data'].str.split(',', expand=True)
        
            # Drop the original 'Data' column
            df.drop('Data', axis=1, inplace=True)
        
            #offset the dates to user timezone
            try:
                #df['Col1'] = pd.to_datetime(df['Col1'], format="%m-%d-%Y %H:%M")
                df['Col1'] = df['Col1'].apply(parse_date)
                df['Col1'] = df['Col1'] - pd.to_timedelta(time_diff_utc, unit='h')
                df['Col1'] = df['Col1'].dt.strftime("%m-%d-%Y %H:%M")
            except:
                pass
            
            ls = df.values.tolist()
        else:
            ls.append(['','',''])

    except:
        ls.append(['', '', ''])
    return np.asarray(ls)



# #This Function retreive the history data for each user
# def get_history(user_ID):

#     firebase3 = pyrebase.initialize_app(config3)
#     db3 = firebase3.database()
#     ls = []
#     try:
#         hist = json.loads(json.dumps(dict(db3.child("USERS").child(user_ID).child("transactionHistory").get().val())))
#         keys_lst = list(hist.keys())
#         for i in range(len(keys_lst)):
#             j = hist[keys_lst[i]].split(",")
#             ls.append([keys_lst[i],j[0],j[1],j[2],j[3],j[4]])
#     except:
#         ls.append(['','','','','',''])
#     return np.asarray(ls)


# def get_billing_history(user_ID):
#     firebase3 = pyrebase.initialize_app(config3)
#     db3 = firebase3.database()
#     ls = []

#     try:
#         hist = json.loads(json.dumps(dict(db3.child("USERS").child(user_ID).child("billingHistory").get().val())))
#         keys_lst = list(hist.keys())

#         for i in range(len(keys_lst)):
#             j = hist[keys_lst[i]].split(",")
#             ls.append([keys_lst[i], j[0], j[1]])
#     except Exception:
#         ls.append(['', '', ''])
#     return np.asarray(ls)
