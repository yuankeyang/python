# -*- coding: UTF8 -*-
from collections import deque
import re
from urllib.request import urlopen
import urllib

queue=deque()
visited=set()
textfile=open('depth_1.txt','wt')
print("Enter the URL you wish to crawl.")
myurl=input(">")

queue.append(myurl)
cnt=0

while queue:
    url=queue.popleft()#队首出队
    visited|={url}#放入访问集合
    cnt+=1
    print('将要访问第'+str(cnt)+'个url:'+url)
    try:
        urlop=urlopen(url,timeout=1)
    except urllib.error.URLError as e:
        print(e)
        continue
    if 'html' not in urlop.getheader('Content-Type'):
        continue
    #捕获异常
    try:
        data=urlop.read().decode('utf-8')
    except:
        continue
    #正则表达式提取页面中url
    linkre=re.compile('href=\"(.+?)\"',re.I)
    for link in linkre.findall(data):
        if 'http' in link and link not in visited:
            queue.append(link)
            print('把'+link+'加入队列')
