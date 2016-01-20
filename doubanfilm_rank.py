#! python3

"""
get douban film rank from bttiantang.com
"""

import urllib.request
import sqlite3
import re
import time
from bs4 import BeautifulSoup

def get_rank(film_id):
    url = 'http://www.bttiantang.com/subject/%d.html' % film_id
    try:
        raw_html = urllib.request.urlopen(url).read().decode('utf-8')
    except TimeoutError:
        return None
    except urllib.error.HTTPError:
        print(film_id,404)
        return None

    soup = BeautifulSoup(raw_html,'lxml')
    rank_em = soup.find_all(class_='rt')
    r = re.search(r'(\d+).*(\d+)',str(rank_em))
    if r:
        rank = int(r.group(1)) * 10 + int(r.group(2))
    else:
        rank = 0
    title = soup.find('h1').string
    if not title: return None
    return (title,rank)

def create_table(conn):
    conn.execute('create table film (id int, name varchar(64), rank short)')
    conn.execute('insert into film (id,name,rank) values (3628,"",0)')
    conn.commit()

if __name__ == '__main__':
    conn = sqlite3.connect('film.db')
    #create_table(conn)
    film_id = conn.execute('select max(id) from film').fetchone()[0]
    while True:
        film_id = film_id + 1
        res = get_rank(film_id)
        if res:
            print(film_id,res)
            conn.execute('insert into film (id,name,rank) values (?,?,?)',(film_id,res[0],res[1]))
            conn.commit()
        #time.sleep(5)
