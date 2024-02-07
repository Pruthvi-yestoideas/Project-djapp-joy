
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from djapp.plugins.domain_val import domain_val, img_logo_link

domain = domain_val()
def contactus(emai, name, subject, message):
    #Some code
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
                <a href="https://www.'''+domain+'''.com" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://www.'''+domain+'''.com/">
                    <img src="'''+img_logo_link()+'''" width="200" border="0" style="vertical-align:middle" class="CToWUd">
                </a>
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
                                            <td class="m_-7075686139613542793content" style="font:16px/22px 'Helvetica Neue',Arial,'sans-serif';text-align:left;color:#F;padding:40px 40px 0px 40px">
                                                <p>
        Hi ''' + str(name) +''',</p>
    <p><strong>Thank you for submitting your ticket. 
    Here's what we received: </strong></p>
    <p></p>
    
    
                                            </td>
                                        </tr>
    
    <tr><td> <br><br> </td></tr>
    
    
    <tr>
        
        
    <td style="WIDTH:100%;PADDING-BOTTOM:20px;PADDING-TOP:20px;PADDING-LEFT:10%;PADDING-RIGHT:10%;BACKGROUND-COLOR:#F3F1EA">
    <p style="FONT-SIZE:13px;FONT-FAMILY:Arial,'open sans',Helvetica,sans-serif;TEXT-ALIGN:center;LINE-HEIGHT:16px"> ''' + str(subject) + '''<br><br>''' + str(message) + '''<br><br></p>
    </td>
    </tr>
    
    <tr>
                                            <td class="m_-7075686139613542793content" style="font:16px/22px 'Helvetica Neue',Arial,'sans-serif';text-align:left;color:#F;padding:40px 40px 0px 40px">
                                                
    <p><strong>Explore our 
        <a href="https://www.'''+domain+'''.com/faq" style="color:#575fff;text-decoration:none" target="_blank" data-saferedirecturl="https://www.'''+domain+'''.com/faq">FAQs</a>
        —you might discover the solution you're seeking—while our dedicated team diligently attends to your inquiry.
    </strong></p>
    
    
    
    <p></p>
    
    <p>
        Thanks,<br>The '''+domain+''' Team
    </p>
                                            </td>
                                        </tr>
    
                                        <tr>
    <td style="WIDTH:100%;PADDING-BOTTOM:20px;PADDING-TOP:20px;PADDING-LEFT:10%;PADDING-RIGHT:10%;BACKGROUND-COLOR:#d9d9d9">
    <p style="FONT-SIZE:13px;FONT-FAMILY:Arial,'open sans',Helvetica,sans-serif;TEXT-ALIGN:center;LINE-HEIGHT:16px"><b>This is an automated response. </b>Feel free to reply to this message if you would like to provide additional information regarding your ticket.<br></p>
    </td>
    </tr>
    
    
    
    
                                        </tbody></table>
                                    </td>
                                </tr>
                                
                                
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
                      <td style="color:#999999;font-size:12px;line-height:16px;text-align:center"><span style="font-family:arial,helvetica neue,helvetica,sans-serif">This is an automatic e-mail
    
    <br> Copyright © ''' + str(datetime.now().year) +''' ''' + domain +''' Inc. All Rights Reserved                  </span>
                      </td>
                   </tr>
                   
                </tbody></table>
                
    </td> </tr>
                            </tbody></table>
                            
                </td>
                </tr>
        </tbody></table></body></html>'''
    
    
    #The mail addresses and password
    sender_address = 'support@'+domain+'.com'
    sender_pass = 'Helloworld66@@@'
    #Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_address
    msg['To'] = emai
    msg['Subject'] = domain + ' Auto Reply'   #The subject line
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






# Email configuration

# Create the email message


# Connect to the SMTP server and send the email
