#!/usr/bin/python3 

import redis
import os
import sys
import tempfile


if __name__ == '__main__':
    r = redis.Redis()
    (_,temp) = tempfile.mkstemp()
    print(temp)
    with open(temp,'w') as fd:
        print('digraph quora_topic {',file=fd)
        for topic in r.smembers('quora:topic'):
            topic = topic.decode('utf-8')
            rtopic = r.get('quora:topic:'+topic)
            if rtopic:
                for rt in rtopic.decode('utf-8').split(','):
                    print('"%s" -> "%s";' % (topic,rt),file=fd)
        print('}',file=fd)

    os.system('dot -x -Tpng %s -oquora_topic.png' % temp)
    os.remove(temp)
          
