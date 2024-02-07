import pyrebase
import numpy as np
import random
np.set_printoptions(threshold=np.inf)
import json
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from eth_account import Account
import secrets
import html
import urllib.parse
import base64
from djapp.plugins.domain_val import domain_val,img_logo_link
from djapp.plugins.config import config0,config1

domain = domain_val()
logo_link = img_logo_link()


###############################################################################################################################
###################################################LOG IN SECTION#####################################################
###############################################################################################################################
###############################################################################################################################
#This function will check if the user credentials is vaid or not
#Then if it's vaid it'll return all the user info which contains the user[localId] & user[displayName]
#and if not vaid will return "invalid credentials"
def user_auth(email,password):

    password = password.replace(" ", "")
    firebase = pyrebase.initialize_app(config0)
    auth = firebase.auth()
    db = firebase.database()

    passes = json.loads(json.dumps(dict(db.child("EMAILS").get().val())))[encode_email(email)].split(",")

    if password == passes[1]:
        #get the google's real password
        password_google = passes[0]
        try:
            user = auth.sign_in_with_email_and_password(email,password_google)
        except:
            user = False
    else:
        user = False
    return user



###############################################################################################################################
###################################################SIGN UP SECTION#####################################################
###############################################################################################################################
###############################################################################################################################

def welcome_email(emai, password, name, domain, logo_link):
    
    mail_content = '''
    <html>
    <head>
        <style>
            .container {
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 40px;
                font-family: 'Helvetica Neue', Arial, sans-serif;
            }
            .header, .footer {
                text-align: center;
                margin-bottom: 20px;
            }
            .content {
                font-size: 16px;
                line-height: 1.5;
                color: #555555;
            }
            .separator {
                border-top: 1px solid #e4e4e4;
                margin: 30px 0;
            }
            a {
                color: #141aff;
                text-decoration: underline;
            }
        </style>
        </head>
        <body bgcolor="#eeeeee">
        <table width="100%" bgcolor="#eeeeee">
            <tr>
                <td align="left">
                    <div class="container">
                        <div class="header">
                            <a href="https://www.'''+domain+'''.com">
                                <img src="'''+logo_link+'''" alt="'''+domain+''' Logo" width="200">
                            </a>
                            <h2>Welcome To '''+domain+'''</h2>
                        </div>
                        <div class="separator"></div>
                        <div class="content">
                            <p>Dear '''+name+''',</p>
                            <p>Welcome to '''+domain+'''. We're excited to have you on board.</p>
                            <p>
                                <a href="https://app.'''+domain+'''.com/">Start shipping now</a>
                            </p>
                            <p>
                                For a comprehensive view of our full pricing list, please visit our dedicated 
                                <a href="https://app.'''+domain+'''.com/pricing.html/">Pricing Page</a>.
                            </p>
                            <p>
                                To better understand how to utilize our system effectively, please refer to the step-by-step 
                                <a href="https://app.'''+domain+'''.com/get-started/">guide</a>.
                            </p>
                            <p>
                                For any additional information, please refer to our comprehensive 
                                <a href="https://app.'''+domain+'''.com/faq/">FAQ section</a> on our website. Should you require further clarification or assistance, please feel free to reach out to us via this email thread.
                            </p>
                            <p>If you fall into technical difficulties or have ideas on how to improve '''+domain+''', don't hesitate to contact us at support@'''+domain+'''.com</p>
                            <p>Thanks, <br> The '''+domain+''' Team</p>
                        </div>
                        <div class="footer">
                            <p style="font-size: 12px; color: #999999;">
                                This is an automatic e-mail and We cannot receive replies to this email address.
                                <br> 
                                Copyright © '''+str(datetime.now().year)+''' '''+domain+''' Inc. All Rights Reserved.
                            </p>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>'''


    sender_address = 'noreply@'+domain+'.com'
    sender_pass = 'Helloworld66@@@'
    #Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_address
    msg['To'] = emai
    msg['Subject'] = 'Welcome To '+domain.upper()   #The subject line
    # Add a BCC recipient
    bcc_recipients = [sender_address]
    msg.add_header('Bcc', ', '.join(bcc_recipients))  
    #The body and the attachments for the mail
    msg.attach(MIMEText(mail_content, 'html'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP_SSL('mail.privateemail.com', 465) #use gmail with port
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = msg.as_string()
    session.sendmail(sender_address, [emai] + bcc_recipients, text)
    session.quit()
    print('Mail Sent')
    

    return True

def updating_balance_email(Name, receiver_address, total, domain, logo_link, signup_gift_amount):
    mail_content = '''<html>
        <head></head>
        <body>
        <table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tbody>
        <tr>
        <td width="100%" align="center" valign="top" bgcolor="#eeeeee" height="20"></td>
        </tr>
        <tr>
        <td bgcolor="#eeeeee" align="center" style="padding:0px 15px 0px 15px" class="m_-7075686139613542793section-padding">
        <table bgcolor="#ffffff" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px" class="m_-7075686139613542793responsive-table">
        <tbody>
        <tr>
        <td>
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody>
        <tr>
        <td align="center" style="padding:40px 40px 0px 40px">
        <a href="https://www.''' + domain + '''.com" target="_blank" data-saferedirecturl="https://www.''' + domain + '''.com">
        <img src="''' + logo_link + '''" alt="''' + domain + ''' Logo" width="200" border="0" style="vertical-align:middle" class="CToWUd">
        </a>
        </td>
        </tr>
        <tr>
        <td align="center" style="font-size:18px;color:#0e0e0f;font-weight:700;font-family:Helvetica Neue;line-height:28px;vertical-align:top;text-align:center;padding:20px 40px 0px 40px">
        <strong>Welcome! Here's Your Sign-Up Gift</strong>
        </td>
        </tr>
        <tr>
        <td align="center" bgcolor="#ffffff" height="1" style="padding:30px 40px 5px" valign="top" width="100%">
        <table cellpadding="0" cellspacing="0" width="100%">
        <tbody>
        <tr>
        <td style="border-top:1px solid #e4e4e4">
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        <tr>
        <td class="m_-7075686139613542793content" style="font:16px/22px 'Helvetica Neue',Arial,'sans-serif';text-align:left;color:#555555;padding:40px 40px 0px 40px">
        <p>
        Dear ''' + str(Name) + ''',</p>
        <p><strong>Welcome to ''' + domain + '''!</strong>
        <br>
        We're thrilled to have you join our community. As a sign-up gift, we've added a bonus of USD ''' + str(signup_gift_amount) + ''' to your account.</p>
        <p>
        Your new balance is: USD ''' + str(total) + '''</p>
        <p>Enjoy your experience with us!</p>
        </td>
        </tr>
        <tr>
        <td>
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin:30px 0px">
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        <tr>
        <td width="100%" align="center" valign="top" bgcolor="#ffffff" height="45"></td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        <tr>
        <td bgcolor="#eeeeee" align="center" style="padding:20px 0px">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" style="max-width:600px" class="m_-7075686139613542793responsive-table">
        <tbody>
        <tr> </tr>
        <tr>
        <td bgcolor="#eeeeee" align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" style="max-width:600px" class="m_-7075686139613542793responsive-table">
        <tbody>
        <tr>
        <td style="color:#999999;font-size:12px;line-height:16px;text-align:center"><span style="font-family:arial,helvetica neue,helvetica,sans-serif">This is an automatic e-mail and We cannot receive replies to this email address.
        <br> Copyright © ''' + str(datetime.now().year) + " " + domain + ''' Inc. All Rights Reserved                  </span>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </td>
        </tr>
        </tbody>
        </table>
        </body>
        </html>'''
    #The mail addresses and password
    sender_address = 'noreply@'+domain+'.com'
    sender_pass = 'Helloworld66@@@'
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = "Account Balance Update: $"+str(signup_gift_amount)+" Added."   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP_SSL('mail.privateemail.com', 465) #use gmail with port
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent2')

    return True


def signup(email,name,ip_add,customer_pass):

    EMAIL = email
    password = randomStringDigits(12).replace(" ", "")
    
    #Create Etherum Wallet
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    public_key = acct.address

    #MainDatabase
    firebase = pyrebase.initialize_app(config0)
    auth = firebase.auth()
    db = firebase.database()
    account_info = auth.create_user_with_email_and_password(EMAIL, password)
    accID = account_info['localId']

    update_data = {
        'data': "0",
        'domain': domain,
        'email_name': EMAIL + "," + name,
        'flag': 0,
        'service_type': "0",
        'size': "0",
        'wallet': public_key,
        'PK': private_key,
        'client_ip': str(ip_add)
    }

    db.child("USERS").child(accID).update(update_data)
    db.child("EMAILS").update({encode_email(EMAIL):str(password)+","+str(password)})

    #get the passes of the client
    passes = json.loads(json.dumps(dict(db.child("EMAILS").get().val())))[encode_email(EMAIL)].split(",")
    # Update the password "Fake one only" 
    db.child("EMAILS").update({encode_email(EMAIL):str(passes[0])+","+str(customer_pass)})


    #get the Pricing
    obj = json.loads(json.dumps(db.child("Pricing").get().val()))

    initial_bal = db.child("Initial_Balance").get().val()
    firebase1 = pyrebase.initialize_app(config1)
    db1 = firebase1.database()

    db1.child(accID).update(obj)
    db1.child(accID).update({'balance': initial_bal})

    #Email the welcoming email to user
    bol = welcome_email(EMAIL, password, name, domain, logo_link)
    if initial_bal>0:
        bol1 = updating_balance_email(name, EMAIL, initial_bal, domain, logo_link, initial_bal)

    return bol


###############################################################################################################################
###################################################FORGET PASSWORD SECTION#####################################################
###############################################################################################################################
###############################################################################################################################

def check_email_exists(em):
    emails = []
    firebase = pyrebase.initialize_app(config0)  # Uncomment this when you run it locally
    db = firebase.database()
    json_db = json.loads(json.dumps(dict(db.get().val()))) #Get All users in the system
    all_user_ids = list(json_db['USERS'].keys())
    for userID in all_user_ids:
        emails.append([json_db['USERS'][userID]['email_name'].split(",")[0], userID])
    email_exist = em in [row[0] for row in emails]
    if email_exist==True:
        return email_exist, json_db['EMAILS'][encode_email(em)].split(",")[0], emails[[row[0] for row in emails].index(em)][1]
    else:
        return email_exist, '', ''


def send_verification_code_email(receiver_address,domain,ver_code):
    mail_content = '''
    <html><head></head><body><table border="0" cellpadding="0" cellspacing="0" width="100%">
            
                    <tbody><tr><td width="100%" align="center" valign="top" bgcolor="#eeeeee" height="20"></td></tr>
                    <tr>
                    <td bgcolor="#eeeeee" align="center" style="padding:0px 15px 0px 15px" class="m_-7075686139613542793section-padding">
                        
                                <table bgcolor="#ffffff" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px" class="m_-7075686139613542793responsive-table">
                                    <tbody><tr>
                                        <td>
                                            
                                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                            
            <tbody><tr>
                <td align="center" style="padding:40px 40px 0px 40px">
                    <a href="https://www.'''+domain+'''.com" target="_blank" data-saferedirecturl="https://www.'''+domain+'''.com">
                        <img src="'''+logo_link+'''" width="200" border="0" style="vertical-align:middle" class="CToWUd">
                    </a>
                </td>
            </tr>
            <tr>
                <td align="center" style="font-size:18px;color:#0e0e0f;font-weight:700;font-family:Helvetica Neue;line-height:28px;vertical-align:top;text-align:center;padding:35px 40px 0px 40px">
                    <strong>Password Reset Request</strong>
                </td>
            </tr>
            
                <tr>
                    <td align="center" bgcolor="#ffffff" height="1" style="padding:40px 40px 5px" valign="top" width="100%">
                        <table cellpadding="0" cellspacing="0" width="100%">
                            <tbody>
                            <tr>
                                <td style="border-top:1px solid #e4e4e4">
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
        
                                            <tr>
                                                <td class="m_-7075686139613542793content" style="font:16px/22px 'Helvetica Neue',Arial,'sans-serif';text-align:left;color:#555555;padding:40px 40px 0px 40px">
                      <div class="content">
      <p>Dear Customer,</p>
      <p>We received a request to reset the password for your account.</p>
      <p>Your Verification Code is: <strong style="color: red; font-size:20px;">''' + str(ver_code) + '''</strong></p>
      <p>Please enter this code in the provided field to proceed with resetting your password.</p>
      <p>If you did not request a password reset, please ignore this email or contact our support team.</p>
    </div>                              
        <p></p>
        
        <p>
            Thanks,<br>The '''+domain+''' Team
        </p>
                                                </td>
                                            </tr>
                                            <tr>
            <td>
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin:30px 0px">
            </table>
           </td>
        </tr>
        
        
                                            </tbody></table>
                                        </td>
                                    </tr>
                                    
                                    <tr><td width="100%" align="center" valign="top" bgcolor="#ffffff" height="45"></td></tr>
                                </tbody></table>
                                
                    </td>
                    </tr>
                    <tr>
                    <td bgcolor="#eeeeee" align="center" style="padding:20px 0px">
                        
                                
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" style="max-width:600px" class="m_-7075686139613542793responsive-table">
                                    <tbody><tr>  </tr>
                                    <tr> 
        <td bgcolor="#eeeeee" align="center">
           
                    
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" style="max-width:600px" class="m_-7075686139613542793responsive-table">
                       <tbody>
                       <tr>
                          <td style="color:#999999;font-size:12px;line-height:16px;text-align:center"><span style="font-family:arial,helvetica neue,helvetica,sans-serif">This is an automatic e-mail and We can’t receive replies to this email address.
        
        <br> Copyright © '''+str(datetime.now().year)+" "+domain+''' Inc. All Rights Reserved                  </span>
                          </td>
                       </tr>
                       
                    </tbody></table>
                    
        </td> </tr>
                                </tbody></table>
                                
                    </td>
                    </tr>
                </tbody></table></body></html>'''
            
    #The mail addresses and password
    sender_address = 'noreply@' + domain + '.com'
    sender_pass = 'Helloworld66@@@'
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = '[Action Required] Reset Your ' + domain.upper() + ' Password'   #The subject line
    # Add a BCC recipient
    bcc_recipients = [sender_address]
    message.add_header('Bcc', ', '.join(bcc_recipients))     #The body and the attachments for the mail
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP_SSL('mail.privateemail.com', 465) #use gmail with port
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, [receiver_address] + bcc_recipients, text)
    session.quit()
    print('Mail Sent')


def password_reset_successful(receiver_address,new_pass,domain):
    #updating auth and database with the new password
    new_pass = new_pass.replace(" ", "")
    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()

    #get the passes of the client
    passes = json.loads(json.dumps(dict(db.child("EMAILS").get().val())))[encode_email(receiver_address)].split(",")
    # Update the password "Fake one only" 
    db.child("EMAILS").update({encode_email(receiver_address):str(passes[0])+","+str(new_pass)})

    #send mails
    mail_content = '''
    <html><head></head><body><table border="0" cellpadding="0" cellspacing="0" width="100%">
            
                    <tbody><tr><td width="100%" align="center" valign="top" bgcolor="#eeeeee" height="20"></td></tr>
                    <tr>
                    <td bgcolor="#eeeeee" align="center" style="padding:0px 15px 0px 15px" class="m_-7075686139613542793section-padding">
                        
                                <table bgcolor="#ffffff" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px" class="m_-7075686139613542793responsive-table">
                                    <tbody><tr>
                                        <td>
                                            
                                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                            
            <tbody><tr>
                <td align="center" style="padding:40px 40px 0px 40px">
                    <a href="https://www.'''+domain+'''.com" target="_blank" data-saferedirecturl="https://www.'''+domain+'''.com">
                        <img src="'''+logo_link+'''" width="200" border="0" style="vertical-align:middle" class="CToWUd">
                    </a>
                </td>
            </tr>
            <tr>
                <td align="center" style="font-size:18px;color:#0e0e0f;font-weight:700;font-family:Helvetica Neue;line-height:28px;vertical-align:top;text-align:center;padding:35px 40px 0px 40px">
                    <strong>Password Reset Successful</strong>
                </td>
            </tr>
            
                <tr>
                    <td align="center" bgcolor="#ffffff" height="1" style="padding:40px 40px 5px" valign="top" width="100%">
                        <table cellpadding="0" cellspacing="0" width="100%">
                            <tbody>
                            <tr>
                                <td style="border-top:1px solid #e4e4e4">
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
        
                                            <tr>
                                                <td class="m_-7075686139613542793content" style="font:16px/22px 'Helvetica Neue',Arial,'sans-serif';text-align:left;color:#555555;padding:40px 40px 0px 40px">
                      <div class="content">
      <p>Dear Customer,</p>
      <p>We are pleased to confirm that your password has been successfully reset.</p>
      <p>If you did not initiate this request, please contact our support team immediately to secure your account.</p>
      <p>We appreciate your attention to maintaining the security of your account.</p>
    </div>                            
        <p></p>
        
        <p>
            Thanks,<br>The '''+domain+''' Team
        </p>
                                                </td>
                                            </tr>
                                            <tr>
            <td>
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin:30px 0px">
            </table>
           </td>
        </tr>
        
        
                                            </tbody></table>
                                        </td>
                                    </tr>
                                    
                                    <tr><td width="100%" align="center" valign="top" bgcolor="#ffffff" height="45"></td></tr>
                                </tbody></table>
                                
                    </td>
                    </tr>
                    <tr>
                    <td bgcolor="#eeeeee" align="center" style="padding:20px 0px">
                        
                                
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" style="max-width:600px" class="m_-7075686139613542793responsive-table">
                                    <tbody><tr>  </tr>
                                    <tr> 
        <td bgcolor="#eeeeee" align="center">
           
                    
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" align="center" style="max-width:600px" class="m_-7075686139613542793responsive-table">
                       <tbody>
                       <tr>
                          <td style="color:#999999;font-size:12px;line-height:16px;text-align:center"><span style="font-family:arial,helvetica neue,helvetica,sans-serif">This is an automatic e-mail and We can’t receive replies to this email address.
        
        <br> Copyright © '''+str(datetime.now().year)+" "+domain+''' Inc. All Rights Reserved                  </span>
                          </td>
                       </tr>
                       
                    </tbody></table>
                    
        </td> </tr>
                                </tbody></table>
                                
                    </td>
                    </tr>
                </tbody></table></body></html>'''
            
    
    #The mail addresses and password
    sender_address = 'noreply@' + domain + '.com'
    sender_pass = 'Helloworld66@@@'
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Your Password Has Been Successfully Reset'   #The subject line
    # Add a BCC recipient
    bcc_recipients = [sender_address]
    message.add_header('Bcc', ', '.join(bcc_recipients))     #The body and the attachments for the mail
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'html'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP_SSL('mail.privateemail.com', 465) #use gmail with port
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, [receiver_address] + bcc_recipients, text)
    session.quit()
    print('Mail Sent')
    mail_content = '''
        <html><head></head><body>
        <strong>Welcome To '''+domain+'''</strong><br><br><br>
        <strong>
            Here's your login credentials:
            </strong>
            <br>
            <strong>
            Email: ''' + str(receiver_address) + '''
                </strong>
            <br>
            <strong>
            Password: ''' + str(new_pass) + '''</strong>
        </body></html>'''
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = sender_address
    message['Subject'] = 'Welcome To '+domain.upper()   #The subject line
    message.attach(MIMEText(mail_content, 'html'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP_SSL('mail.privateemail.com', 465) #use gmail with port
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, sender_address, text)
    session.quit()
    print('Mail Sent')

   
###############################################################################################################################
###################################################OTHER FUNCTIONS SECTION#####################################################
###############################################################################################################################
###############################################################################################################################



def randomStringDigits(stringLength):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


#this function will encode email to be put in firebase database
def encode_email(email_body, charset='utf-8'):
    # Step 1: HTML Encoding
    html_encoded = html.escape(email_body)
    
    # Step 2: URL Encoding
    url_encoded = urllib.parse.quote_plus(html_encoded)
    
    # Step 3: Base64 Encoding
    base64_encoded = base64.b64encode(url_encoded.encode(charset)).decode(charset)
    
    # The encoded email body
    return base64_encoded

#Disable website for maintenance
def maintenance_website():
   
    firebase = pyrebase.initialize_app(config0)
    db = firebase.database()
    sys_flag = db.child("sys_flag").get().val()
    if(sys_flag == 1):
        return True
    else:
        return False


#This Function will take the user[localId] and update the login time of the user to google sheets
def post_timestamp(user_ID):
#    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
#    credentials = ServiceAccountCredentials.from_json_keyfile_name('djapp/plugins/creds.json',scope) # get email and key from creds
#    gc = gspread.authorize(credentials)
#    sheet = gc.open_by_key("1OaG3fwTWfhEyEuxwnpsZDKUV_ZaAHqlrSn4WJWoPbOo").worksheet("login")
#    index = len(np.asarray(sheet.get_all_values()))+1
#
#    cell_list = sheet.range('A'+str(index)+':B'+str(index))
#    cell_values = [str(user_ID),str(datetime.datetime.timestamp(datetime.datetime.now()))]
#    for i, val in enumerate(cell_values):  #gives us a tuple of an index and value
#        cell_list[i].value = val    #use the index on cell_list and the val from cell_values
#    sheet.update_cells(cell_list)
    print("d")
