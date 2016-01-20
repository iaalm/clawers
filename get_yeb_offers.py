#!/usr/bin/python3 

"""
get taobao's yu'e'bao offer price
"""

import urllib.request
import re
import time
import sqlite3
from bs4 import BeautifulSoup
import paho.mqtt.client as mqtt
def getAskedQuote(month):
    try:
        raw_html = urllib.request.urlopen('https://zhaocaibao.alipay.com/pf/productQuery.htm?pageNum=1&minMonth=%d&maxMonth=%d&minAmount=&danbao=1'% (month, month+1)).read().decode('gbk')
    except TimeoutError:
        return None

    soup = BeautifulSoup(raw_html,'lxml')
    price_list = soup.find_all(class_='w180')
    price_str = re.findall(r'\d+\.\d+%',str(price_list))
    price = [float(p[:-1]) for p in price_str]
    if len(price):
        return (max(price),min(price))
    else:
        return (None,None)

def createTable(conn):
    conn.execute('create table asked_quote(time int,month int,max_price decimal(5,3),min_price decimal(5,3))')

if __name__ == '__main__':
#    client = mqtt.Client()
#    client.connect("127.0.0.1", 1883, 60)
    conn = sqlite3.connect('offer.db')
    #createTable(conn)
    while True:
        for i in range(24):
            get_time = time.time() 
            price = getAskedQuote(i)
            if not price:
                continue
            print(time.strftime('%H:%M:%S',time.localtime(get_time)),i,price)
#            client.publish('$summary/yeb/%d'%i,str(price))
            ret = conn.execute('INSERT INTO asked_quote(time,month,max_price,min_price) values (?,?,?,?)',(get_time,i,price[0],price[1]))
            conn.commit()
            time.sleep(60)
