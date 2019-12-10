# pyscraper for Amazon
# based on https://www.youtube.com/watch?v=Bg9r_yLk7VY
# adapted by Ingo Hinterding
# https://github.com/Esshahn
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



def check_price(URL,desired_price,email,password):

  headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

  page = requests.get(URL, headers=headers)
  soup = BeautifulSoup(page.content, 'html.parser')

  title = soup.find(id="productTitle").get_text().strip()
  price_string = soup.find(
      id="priceblock_ourprice").get_text().strip()

  # convert the currency string to a rounded number
  # this needs to be adapted to your local currency notation
  price = round(float(price_string[:-2].replace(".", "").replace(",", ".")))

  print ("\n----------------------------\n")
  print(title)
  print(f"Current price is: {price_string}")
  print(f"Price alarm at: {desired_price}")

  if (price <= desired_price):
    print(f"Sending price alarm to {email}")
    send_mail( title , price_string , desired_price, URL , email , password )
  else:
    print("No alarm.")



# send email 
def send_mail( title , price , desired_price, URL , email , password):
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(email, password)

  subject = f'Price alarm: {price} for {title[0:40]}...'
  body = "A product you're watching has dropped in price:\n\n"
  body += title + "\n\n"
  body += f"Current price is: {price} (alarm set at {desired_price})\n\n"
  body += URL
  msg = f"Subject: {subject}\n\n{body}"
  
  server.sendmail(
    email,
    email,
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
    check_price(p['url'], p['price'],json_data['email'],json_data['password'])



def main():
  cls()
  scraper(load_json())
  



## -------------- main -------------- ##

main()

