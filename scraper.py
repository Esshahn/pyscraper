# pyscraper for Amazon
# based on https://www.youtube.com/watch?v=Bg9r_yLk7VY
# adapted by Ingo Hinterding
# https://github.com/Esshahn/pyscraper
#
# The script takes a JSON file containing URLs of products on Amazon
# and a desired price to check for. If the current price is equal or
# lower than the desired price, it sends an email to the specified account.
#
# install
# pip3 install requests bs4
#
# run directly
# python3 pyscraper.py
#
# configure
# edit the file products.json to add or remove product URLs and prices


import requests
import sys, re, json
import smtplib
from datetime import datetime
from bs4 import BeautifulSoup


# loads the json file
def load_json():
  with open(sys.path[0] + '/products.json') as json_file:
    return json.load(json_file)


def scraper(json_data):
  for p in json_data['products']:
    search_object = {}
    search_object['url'] = p['url']
    search_object['price'] = p['price']
    search_object['email_from'] = json_data['email_from']
    search_object['email_from_password'] = json_data['email_from_password']

    # if a product entry has an email, use that one instead of the default
    if "email" in p:
      search_object['email_to'] = p['email']
    else:
      search_object['email_to'] = json_data['email_to_default']

    check_price(search_object)


################################
# check the price on the website
################################
def check_price(search_object):

  headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

  page = requests.get(search_object['url'], headers=headers)
  soup = BeautifulSoup(page.content, 'html.parser')

  title = soup.find(id="productTitle").get_text().strip()

  # these are the css IDs of the price on the Amazon website
  price_strings = {"priceblock_ourprice",
                   "priceblock_dealprice", "priceblock_saleprice"}

  # check if any of the price IDs matches
  for string in price_strings:
    result = soup.find(id=string)

    if result is not None:
      price_string = result.get_text().strip()
      break

  print(title)

  if result is not None:
    # convert the currency string to number
    # this needs to be adapted to your local currency notation
    price = float(re.sub(r'\W+', '', price_string))/100

    print(f"Current price is: {price_string}")
    print(f"Price alarm at: {search_object['price']}")

    if (price <= search_object["price"]):
      print(f"Sending price alarm to {search_object['email_to']}")
      search_object["title"] = title
      search_object["price_string"] = price_string
      send_mail(search_object)
    else:
      print("No alarm.")

  else:

    print("No price information found. The link might be wrong or outdated.")
    search_object["title"] = title
    search_object["price_string"] = None
    send_mail(search_object)

  print("\n-----\n")


################################
# send email
################################
def send_mail(search_object):
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(search_object['email_from'],
               search_object['email_from_password'])

  if search_object['price_string'] is not None:
    subject = f"Price alarm: {search_object['price_string']} for {search_object['title'][0:40]}..."
    body = "A product you're watching has dropped in price:\n\n"
    body += search_object['title'] + "\n\n"
    body += f"Current price is: {search_object['price_string']} (alarm set at {search_object['price']})\n\n"
    body += search_object['url']
    msg = f"Subject: {subject}\n\n{body}"
  else:
    subject = f"Please check product {search_object['title'][0:40]}..."
    body = "The script was unable to find a price information for\n\n"
    body += search_object['title'] + "\n\n"
    body += f"Please check the link and update the products.json file if needed.\n\n"
    body += search_object['url']
    msg = f"Subject: {subject}\n\n{body}"

  server.sendmail(
      search_object['email_from'],
      search_object['email_to'],
      msg.encode("utf8"))

  server.quit()


## -------------- main -------------- ##

print("\n\n",datetime.now().strftime("%Y/%m/%d %H:%M:%S"), " ----------------------------\n")
scraper(load_json())

