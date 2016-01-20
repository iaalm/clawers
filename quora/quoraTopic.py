from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
import time
import os
import sys
import re
import redis

def crawlTopic(r):

    # Starting node link
    topic_set = 'quora:topic'
    topic_queue = 'quora:queue'
    if not r.llen(topic_queue):
        start_topic = 'Books'
        r.sadd(topic_set,start_topic)
        r.rpush(topic_queue,start_topic)
    url_t = 'http://www.quora.com/topic/%s'


    browser = webdriver.Chrome()
    browser.set_page_load_timeout(120)
    while r.llen(topic_queue):
        now_topic = r.rpop(topic_queue).decode('utf-8')
        try:
            url = url_t % now_topic
            print(url)

            chromedriver = "chromedriver"   # Needed?
            os.environ["webdriver.chrome.driver"] = chromedriver    # Needed?
            browser.get(url)

            # Fetch /about page
            src_updated = browser.page_source
            src = ""
            count = 0
            while src != src_updated:
                soup = BeautifulSoup(src_updated,"lxml")
                raw_topics = soup.find_all(class_="RelatedTopicsListItem")
                topics=[t.attrs['href'].split('/')[2] for t in raw_topics ]
                if len(topics) != 0:
                    break

                # more
                count = count + 0.5
                if count > 30:
                    break
                time.sleep(.5)
                src = src_updated
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                src_updated = browser.page_source

          #  browser.find_element_by_class_name('expand_link').click()

            if len(topics) == 0:
                r.lpush(topic_queue,now_topic)
                print('sleep 300')
                time.sleep(300)
                continue

            print(topics)
            r.set('quora:topic:%s' % now_topic , ','.join(topics))
            for t in topics:
                if r.sadd(topic_set,t):
                    r.rpush(topic_queue,t)
        except TimeoutException:
            print('timeout!')
            r.lpush(topic_queue,now_topic)

        except:# KeyboardInterrupt
            r.rpush(topic_queue,now_topic)
            browser.quit()
            sys.exit(0)
    browser.quit()

if __name__ == "__main__":
    r = redis.Redis()
    display = Display(visible=0,size=(800,600))
    display.start()
    crawlTopic(r)
    display.stop()
