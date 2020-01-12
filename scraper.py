
#                                                          
#  __ \   |   |   __|   __|   __|  _` |  __ \    _ \   __| 
#  |   |  |   | \__ \  (     |    (   |  |   |   __/  |    
#  .__/  \__, | ____/ \___| _|   \__,_|  .__/  \___| _|    
# _|     ____/                          _|                 
#
#
# Python website scraper that checks for prices
# on Amazon and the Nintendo Store
# based on https://www.youtube.com/watch?v=Bg9r_yLk7VY
# adapted by Ingo Hinterding
# https://github.com/Esshahn/pyscraper


import requests
import sys, re, json, random
import smtplib
from datetime import datetime
from bs4 import BeautifulSoup



def load_JSON(filename):
    # load JSON
    with open(sys.path[0] + '/' + filename) as json_file:
        json_data =  json.load(json_file)
    return json_data



def check_prices(items):
    for item in items["products"]:
        email_to = item["email"] if "email" in item else email["email_to_default"]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.' + str(random.randint(0, 1000))}

        page = requests.get(item["url"], headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.find("title").get_text().strip()

        if ".amazon." in item["url"]:
            price = check_amazon(soup)

        if ".nintendo." in item["url"]:
            price = check_nintendo(soup, page, headers)

        print('\n-----\n' + title)
        print(f'Price: {price}, alarm at {item["price"]}')

        if price is not None:
            if (price <= item["price"]):
                print(f'Sending email to {email_to}')
                item["price_string"] = price
                msg = create_mail_alarm(title, item["price_string"], item["price"], item["url"])
                send_mail(msg, email_to, email["email_from"], email["email_from_password"],
                          email["email_from_smtp"], email["email_from_port"])
            else:
                print('No alarm.')
        else:
            print('No price information found. The link might be wrong or outdated.')
            print(f'Sending email to {email_to}')
            msg = create_mail_error(title, item["url"])
            send_mail(msg, email_to, email["email_from"], email["email_from_password"], email["email_from_smtp"], email["email_from_port"])



def check_amazon(soup):

    # these are the css IDs of the price on the Amazon website
    price_strings = {"priceblock_ourprice", "priceblock_dealprice", "priceblock_saleprice"}

    # check if any of the price IDs matches
    for string in price_strings:
        result = soup.find(id=string)

        if result is not None:
            price_string = result.get_text().strip()
            break

    if result is not None:
        # convert the currency string to number
        # this needs to be adapted to your local currency notation
        price = float(re.sub(r'\W+', '', price_string))/100
        return price

    

def check_nintendo(soup, page, headers):

    # the price is loaded via ajax and needs to be parsed separately
    # to get the correct url of the script, we find a specific variable "offdeviceNsuID"
    # and geth the ID. This is done in a very hacky way as you can see below

    nsuid_pos = str(page.content).find("offdeviceNsuID")+18
    game_id = str(page.content)[nsuid_pos:nsuid_pos+14]
    ajax_url = "https://api.ec.nintendo.com/v1/price?country=DE&lang=de&ids=" + game_id
    json = requests.get(ajax_url, headers=headers).json()

    try:
        price = float(json["prices"][0]["discount_price"]["raw_value"])
    except:
        price = float(json["prices"][0]["regular_price"]["raw_value"])

    return price




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

email = load_JSON('email.json')

items = load_JSON('amazon.json')
check_prices(items)
items = load_JSON('nintendo.json')
check_prices(items)

