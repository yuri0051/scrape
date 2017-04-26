#!/usr/bin/python

import requests
from lxml import html
from datetime import datetime
from pymongo import MongoClient

def spider(url):
    r = requests.get(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'},
    )
    return r

def csv_file():
    date = datetime.utcnow().strftime('%Y_%m_%d')
    fn = 'retailmenot_%s.csv' % date
    header = 'brand,offer,details,url,date_time\n'
    fh = open(fn, 'w')
    fh.write(header)
    return fh

def mongo_db():
    profile = "mongodb://mongodb0.example.net:27017"
    client = MongoClient()
    db = client.retailmenot
    coll = db.dataset
    return client, coll

def scraping1(response, fh, coll):
    data = html.fromstring(response.text)
    elements = data.xpath('.//div[@class="js-recommended-merchant recommended-merchant"]')
    for e in elements:
        item = dict()
        item['brand'] = e.xpath('./div/img/@alt')[0].replace('Coupons', '').strip()
        item['offer'] = e.xpath('./div')[1].text.replace('\n', ' ').strip()
        item['details'] = ''
        item['url'] = ''
        item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        coll.insert(item)
        line = '"%s","%s","%s","%s",%s\n' % (item['brand'], item['offer'], item['details'], item['url'], item['timestamp'])
        fh.write(line)

def scraping2(response, fh, coll):
    data = html.fromstring(response.text)
    elements = data.xpath('.//ul[@class="coupon-list js-offers"]/li')
    for e in elements:
        item = dict()
        item['brand'] = e.xpath('.//div[contains(@class, "offer-merchant-name")]/text()')[0].strip().encode('utf8')
        item['offer'] = e.xpath('.//a[contains(@class, "offer-title")]/text()')[0].strip().encode('utf8')
        item['details'] = e.xpath('.//div[@class="offer-description"]/text()')[0].replace('\n', ' ').strip().encode('utf8')
        item['url'] = e.xpath('.//a/img/@data-merchant-name')[0]
        item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        coll.insert(item)
        line = '"%s","%s","%s","%s",%s\n' % (item['brand'], item['offer'], item['details'], item['url'], item['timestamp'])
        fh.write(line)

def scraping3(response, fh, coll):
    data = html.fromstring(response.text)
    elements = data.xpath('.//div[@class="carousel-slide js-carousel-slide js-triggers-outclick"]')
    for e in elements:
        item = dict()
        item['brand'] = e.xpath('./@data-site-title')[0].strip().encode('utf8')
        item['offer'] = e.xpath('./a/img/@alt')[0].strip().encode('utf8')
        item['details'] = e.xpath('./a/div/div/p/text()')[0].replace('\n', ' ').strip().encode('utf8')
        item['url'] = e.xpath('./@data-merchant-name')[0]
        item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        coll.insert(item)
        line = '"%s","%s","%s","%s",%s\n' % (item['brand'], item['offer'], item['details'], item['url'], item['timestamp'])
        fh.write(line)

def main():
    url = 'https://www.retailmenot.com/'
    response = spider(url)
    fh = csv_file()
    client, coll = mongo_db()
    scraping1(response, fh, coll)
    scraping2(response, fh, coll)
    scraping3(response, fh, coll)
    fh.close()
    client.close()

main()