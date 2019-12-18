![alt text](https://github.com/Esshahn/pyscraper/blob/master/email-screenshot.png "E-Mail")


```

                                                          
  __ \   |   |   __|   __|   __|  _` |  __ \    _ \   __| 
  |   |  |   | \__ \  (     |    (   |  |   |   __/  |    
  .__/  \__, | ____/ \___| _|   \__,_|  .__/  \___| _|    
 _|     ____/                          _|                 

```

# pyscraper
A python script scraping product websites on Amazon that will send you an email if a defined price is reached.

based on https://www.youtube.com/watch?v=Bg9r_yLk7VY
and adapted by Ingo Hinterding


The script takes a JSON file containing URLs of products on Amazon and a desired price to check for. If the current price is equal or lower than the desired price, it sends an email to the specified account.

Note that the price scraped from the website is converted based on german currency notation, e.g. "1.234,56 €". 
You might want to adapt it to your currency notation.

## install
`pip3 install requests bs4`

## run directly
`python3 pyscraper.py`

# configure products.json
Edit the file `products.json` to add or remove product URLs and prices

`"email_from": "your_sender_email@example.com"`

Fill in an email address from where the emails will be send

`"email_from_password": "your_sender_password"`

Fill in the password for the sender email address

`"email_from_smtp": "smtp.gmail.com"`

The SMTP server of your email provider, e.g. Google Mail

`"email_from_port": 587`

The port number of your email provider

`"email_to_default": "your_default_email@example.com"`

Where emails get send to by default (execptions can be made per product). This can be the same email address you specify above, if you're using the script just for yourself.

```
"products": [
    {
      "url": "https://www.amazon.de/Hellblade-Senuas-Sacrifice-PlayStation-4/dp/B07JH57258/ref=sr_1_2?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&keywords=hellblade&qid=1575971001&s=videogames&sr=1-2",
      "price": 29,
      "email": "email_goes_to@example.com"
    }
```

`url` 

Insert the URL to the product you want to track (it doesn't matter if the query changes or has extra data as long as the website ist displayed correctly)

`price`

The desired price of the product. Integer number. The script will send an email if the price is equal or lower.

`email` (optional, remove if not needed)

You can add this line if you want to send the alarm to a different email address. Great if you want to share this script with friends.


## configure your email account
watch the youtube video for a good start how to configure gmail

https://www.youtube.com/watch?v=Bg9r_yLk7VY

Add your email and password to `products.json`


# setup a cronjob (e.g. on Raspberry Pi)
good tutorial here: https://medium.com/@gavinwiener/how-to-schedule-a-python-script-cron-job-dea6cbf69f4e

`crontab -e`

Add a line, e.g. mine is (every day at 14:55)

`55 14 * * * /usr/bin/python3 /home/pi/code/scraper/scraper.py >> /home/pi/code/scraper/log.txt`


# HELP!!!1
I'm by no means a Python or Linux expert, but I'm happy to help if you create an issue.


# Version History

## 1.10

- a complete rewrite with everything shuffled around
- in an attempt to clean the code I probably made it worse... :)
- nah, guess we're fine...
- migrated SMTP and PORT information from code to JSON file where it belongs
- abstracted the functions better

## 1.02

- Some (very basic) error handling is added for when no price was found (you'll be informed by email, too)
- removed terminal clear command and added timestamp output so that it can write to a log file (log.txt)

## 1.01

- a different price formatting approach should work better with multiple currencies
- checking for more CSS tags on Amazon's product website
- sender and recipient emails can now be different
- you can specify a different email for each product search

## 1.0

- initial release

