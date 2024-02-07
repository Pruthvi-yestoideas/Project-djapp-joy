
domain_name = 'apebornfitness'  # Replace this with your actual domain name
logo_img_link = 'https://firebasestorage.googleapis.com/v0/b/maindatabase-c3bfe.appspot.com/o/logo33.png?alt=media&token=5e3ec283-5c74-4cd1-be99-7b00c711f2b0' #the logo with favicon beside it
favicon_img_link = 'https://firebasestorage.googleapis.com/v0/b/maindatabase-c3bfe.appspot.com/o/Favicon5.png?alt=media&token=1f85c777-5929-40fc-9d0b-a9918e3301d8' #the favicon alone
usps_key = '5K2305PARRL89'

def domain_val():
    return domain_name


def img_logo_link():
    return logo_img_link


def domainVal(request):
    return {'domain_name': domain_name}


def imgLogoLink(request):
    return {'logo_img_link': logo_img_link}


def faviconLogoLink(request):
    return {'favicon_img_link': favicon_img_link}
