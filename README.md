# pyscraper
A python script scraping product websites on Amazon that will send you an email if a defined price is reached.

based on https://www.youtube.com/watch?v=Bg9r_yLk7VY
adapted by Ingo Hinterding


The script takes a JSON file containing URLs of products on Amazon
and a desired price to check for. If the current price is equal or
lower than the desired price, it sends an email to the specified account.

Note that the price scraped from the website is converted based on 
german currency notation, e.g. "1.234,56 €"
You might want to adapt it to your currency notation

# install
`pip3 install requests bs4`

# run directly
`python3 pyscraper.py`

# configure
edit the file `products.json` to add or remove product URLs and prices

# configure your email
watch the youtube video for a good start how to configure gmail
https://www.youtube.com/watch?v=Bg9r_yLk7VY
Add your email and password to `products.json`

# setup a cronjob (e.g. on Raspberry Pi)
good tutorial here: https://medium.com/@gavinwiener/how-to-schedule-a-python-script-cron-job-dea6cbf69f4e
`crontab -e`
add a line, e.g. mine is (every day at 14:55)
`55 14 * * * /usr/bin/python3 /home/pi/code/scraper/scraper.py`
