
#                                                          
#  __ \   |   |   __|   __|   __|  _` |  __ \    _ \   __| 
#  |   |  |   | \__ \  (     |    (   |  |   |   __/  |    
#  .__/  \__, | ____/ \___| _|   \__,_|  .__/  \___| _|    
# _|     ____/                          _|                 
#
#
# pyscraper for Amazon
# based on https://www.youtube.com/watch?v=Bg9r_yLk7VY
# adapted by Ingo Hinterding
# https://github.com/Esshahn/pyscraper


import requests
import sys, re, json
import smtplib
from datetime import datetime
from bs4 import BeautifulSoup



def load_JSON(filename):
    # load JSON
    with open(sys.path[0] + '/' + filename) as json_file:
        json_data =  json.load(json_file)

    return json_data




def check_price(item,email_to):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

    page = requests.get(item["url"], headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    title = soup.find(id="productTitle").get_text().strip()

    # these are the css IDs of the price on the Amazon website
    price_strings = {"priceblock_ourprice",
                     "priceblock_dealprice", 
                     "priceblock_saleprice"}

    # check if any of the price IDs matches
    for string in price_strings:
        result = soup.find(id=string)

        if result is not None:
            price_string = result.get_text().strip()
            break

    print('\n-----\n' + title)
    item["title"] = title

    if result is not None:
        # convert the currency string to number
        # this needs to be adapted to your local currency notation
        price = float(re.sub(r'\W+', '', price_string))/100

        print(f'Price: {price_string}, alarm at {item["price"]}')

        if (price <= item["price"]):
            print(f'Sending email to {email_to}')
            item["price_string"] = price_string
            return item
        else:
            print('No alarm.')
        
    else:
        print('No price information found. The link might be wrong or outdated.')
        print(f'Sending email to {email_to}')
        return item
    



def create_mail_alarm(title,price_string,price,url):

    subject = f'Price alarm: {price_string} for {title[0:40]}...'
    body = "A product you're watching has dropped in price:\n\n"
    body += title + '\n\n'
    body += f'Current price is: {price_string} (alarm set at {price})\n\n'
    body += url
    msg = f'Subject: {subject}\n\n{body}'

    return msg




def create_mail_error(title,url):

    subject = f'Please check product {title[0:40]}...'
    body = 'The script was unable to find a price information for\n\n'
    body += title + "\n\n"
    body += f'Please check the link and update the products.json file if needed.\n\n'
    body += url
    msg = f'Subject: {subject}\n\n{body}'

    return msg




def send_mail(msg, email_to, email_from, email_from_password, email_from_smtp, email_from_port):
    server = smtplib.SMTP(email_from_smtp, email_from_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_from, email_from_password)
    server.sendmail(email_from, email_to, msg.encode('utf8'))
    server.quit()



## -------------- main -------------- ##

print('\n\n',datetime.now().strftime('%Y/%m/%d %H:%M:%S'), ' ----------------------------\n')

items = load_JSON('products_amazon.json')
email = load_JSON('email.json')

for item in items["products"]:
    email_to = item["email"] if "email" in item else email["email_to_default"]  
    result = check_price(item,email_to)
    
    if result:
        if "price_string" in result:
            msg = create_mail_alarm(item["title"],
                                    item["price_string"],
                                    item["price"],
                                    item["url"])
        else:
            msg = create_mail_error(item["title"],
                                    item["url"])
        
        send_mail(msg,
                  email_to, 
                  email["email_from"], 
                  email["email_from_password"], 
                  email["email_from_smtp"], 
                  email["email_from_port"])
