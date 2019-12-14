# pyscraper for Amazon
# based on https://www.youtube.com/watch?v=Bg9r_yLk7VY
# adapted by Ingo Hinterding
# https://github.com/Esshahn/pyscraper
#
# The script takes a JSON file containing URLs of products on Amazon
# and a desired price to check for. If the current price is equal or
# lower than the desired price, it sends an email to the specified account.
#
# Note that the price scraped from the website is converted based on 
# german currency notation, e.g. "1.234,56 €"
# You might want to adapt it to your currency notation
#
# install
# pip3 install requests bs4
#
# run directly
# python3 pyscraper.py
#
# configure
# edit the file products.json to add or remove product URLs and prices
#
# configure your email
# watch the youtube video for a good start how to configure gmail
# https://www.youtube.com/watch?v=Bg9r_yLk7VY
# Add your email and password to products.json
#
# setup a cronjob (e.g. on Raspberry Pi)
# good tutorial here: https://medium.com/@gavinwiener/how-to-schedule-a-python-script-cron-job-dea6cbf69f4e
# crontab -e
# add a line, e.g. mine is (every day at 14:55)
# 55 14 * * * /usr/bin/python3 /home/pi/code/scraper/scraper.py




import requests
import json
import sys, os
from bs4 import BeautifulSoup
import smtplib



def check_price(search_object):

  headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

  page = requests.get( search_object['url'] , headers=headers )
  soup = BeautifulSoup( page.content, 'html.parser' )

  title = soup.find(id="productTitle").get_text().strip()
  price_string = soup.find(
      id="priceblock_ourprice").get_text().strip()

  # convert the currency string to a rounded number
  # this needs to be adapted to your local currency notation
  price = round(float(price_string[:-2].replace(".", "").replace(",", ".")))

  print ("\n----------------------------\n")
  print(title)
  print(f"Current price is: {price_string}")
  print(f"Price alarm at: {search_object['price']}")

  if (price <= search_object["price"]):
    print(f"Sending price alarm to {search_object['email_to']}")
    search_object["title"] = title
    search_object["price_string"] = price_string
    send_mail( search_object )
  else:
    print("No alarm.")



# send email 
def send_mail( search_object ):
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(search_object['email_from'], search_object['email_from_password'])

  subject = f"Price alarm: {search_object['price_string']} for {search_object['title'][0:40]}..."
  body = "A product you're watching has dropped in price:\n\n"
  body += search_object['title'] + "\n\n"
  body += f"Current price is: {search_object['price_string']} (alarm set at {search_object['price']})\n\n"
  body += search_object['url']
  msg = f"Subject: {subject}\n\n{body}"
  
  server.sendmail(
    search_object['email_from'],
    search_object['email_to'],
    msg.encode("utf8"))

  server.quit()



# clears the terminal
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')



# loads the json file
def load_json():
  with open(sys.path[0] + '/products.json') as json_file:
    return json.load(json_file)
    
    

def scraper(json_data):
  for p in json_data['products']:
    search_object = {}
    search_object['url'] = p['url']
    search_object['price'] = p['price']
    search_object['email_from'] = json_data['email_from'];
    search_object['email_from_password'] = json_data['email_from_password']
    if "email" in p:
      search_object['email_to'] = p['email']
    else:
      search_object['email_to'] = json_data['email_to_default']

    check_price(search_object)



def main():
  cls()
  scraper(load_json())
  



## -------------- main -------------- ##

main()

