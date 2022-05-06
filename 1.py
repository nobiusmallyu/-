# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
import re

'''
python 3
1.url管理器 UrlManager
  管理新URL、旧URL (元组)
  添加一个URL到新URL，要求不在新URL和旧URL里
  接收多个URL，调用上一步
  检测是否有新的URL
  获取一个新的URL，从新URL弹出一个到旧URL

2.html下载器 HtmlDownLoader
  requests get方式访问URL，如果状态码不是200就返回HTML内容

3.html解析器 HtmlParser
  urlparse解析出域名
  内部实现一个元组存放解析出来的新URL，从BeautifulSoup对象提取所有a标签里的href地址，判断是否是当前域名下的链接，如果不是就跳过(可以另存起来作为外链)，将上一层URL与提取出来的URL合并，写入内部的新URL，就是当前页面所提取出来的URL
  解析HTML内容调用 parse 函数

4.爬虫主程序 SpiderMain
  初始化一个URL管理器、HTML下载器、HTML解析器
  定义一个爬行函数，接收一个URL作为起始路径

5.main函数
  定义起始URL
  实例化爬虫主程序对象
  将起始URL作为参数传入爬虫对象的爬行函数，开始爬行
'''


class UrlManager:
    def __init__(self):
        self.new_urls = set()  # 存放新的URL，将被访问并解析response里的新链接，递归下去，直到没有新的URL存进来就退出整个程序
        self.old_urls = set()  # 存在已经爬取的，且属于本站的链接

    def add_new_url(self, url):
        if url is None:
            return None
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)

    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return None
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        return len(self.new_urls) != 0  # 返回新URL元组是否为空，False(不为空)或True(空)，空表示没有新的URL需要爬行了，会退出主程序

    def get_new_url(self):
        new_url = self.new_urls.pop()  # 从新URL元组中取一个URL
        self.old_urls.add(new_url)  # 把它移到旧的URL数组，
        return new_url


class HtmlDownLoader():
    def download(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36'}

        if url is None:
            return None
        else:
            r = requests.get(url,headers=headers)
        if r.status_code != 200:
            return None
        else:
            
            return r.text


class HtmlParser:
    def __init__(self):
        self.foreign_urls = set()        
        
        #判断当前url的服务器
    def _get_root_domain(self, url):
        # 是否应该在这里用正则判断传进来的URL是/开头，如果解析出来netloc是空，那也算是当前域名的链接
        if url is None:
            return None
        url_info = urlparse(url)
        root_domain = url_info.netloc
        return root_domain

    def _get_new_urls(self, soup, current_url):
        new_urls = set()
        #获取网页内容中的a标签
        links = soup.find_all("a")
        
        #遍历a标签中的href
        for link in links:
            new_url = link.get('href')

            #去除url中的空格
            if new_url is not None:
                new_url = new_url.lstrip()
            new_url_root_domain = self._get_root_domain(new_url)
            #如果服务器为空pass
            if new_url_root_domain == '':
                pass
            #如果有服务器再判断这个服务器与当前网页url的服务器是否一样
            elif new_url_root_domain is not None:
                if self._get_root_domain(current_url) != self._get_root_domain(new_url):
                    continue
            # elif new_url_root_domain is None:
            #     pass
            #将href和当前url拼接
            new_full_url = urljoin(current_url, new_url)
            
            #存入new_urls
            new_urls.add(new_full_url)

        return new_urls

    def parse(self, html_content, current_url):
        if html_content is None:
            return
        soup = BeautifulSoup(html_content, "html.parser")
        new_urls = self._get_new_urls(soup, current_url)
        return new_urls

    def get_foreign_urls(self):
        return self.foreign_urls

# 核心类
class SpiderMain:
    #继承上面的类
    def __init__(self):
        self.urls = UrlManager()
        self.html_downloader = HtmlDownLoader()
        self.parser = HtmlParser()
    #将主域名中的子域名写入到指定文件中
    def craw(self, root_url):
        
        #将传入的url进行判断，如果不在new_urls和old_urls中，就将其加入到new_urls
        self.urls.add_new_url(root_url)
        #循环判断如果new_urls里面没有元素了，说明该网站的所有的子域名已经爬完
        while self.urls.has_new_url():
            #将new_urls里面提取出一个放入old_urls中
            new_url = self.urls.get_new_url()
            try:
                #将当前放入old_urls中的url，进行get请求，如果返回200获取网页内容
                html_content = self.html_downloader.download(new_url)
                #提取页面内容中的a标签当中的href，并且与当前url拼接
                new_urls = self.parser.parse(html_content, new_url)
                #将拼接好的新url存入new_urls中
                self.urls.add_new_urls(new_urls)
                #将子域名都写入到txt中
                with open('./1.txt','a') as f:
                    f.write(new_url+'\n')
                print ("craw %s" % new_url)  
            except:
                print ("failed %s" % new_url)
        print (len(self.urls.old_urls), self.urls.old_urls)
        print (len(self.parser.foreign_urls), self.parser.foreign_urls)
        


if __name__ == "__main__":
    new_sqlmap_urls = set()
    with open('./url.txt') as fp:
        for u in fp:
            u = u.strip('\r\n')
            with open('./1.txt','w') as f:
                pass
            
            if '://' in u:
                root_url = u 
            else:
                 root_url = 'https://' + u
            obj_spider = SpiderMain()
            obj_spider.craw(root_url)

    
    with open('./1.txt','r',encoding='utf-8') as e:
            lines = e.readlines()
            for line in lines:
                if "?" in line:
                    new_sqlmap_urls.add(line)
                    print(new_sqlmap_urls)
                else:
                    pass
    with open('./end.txt','w+') as en:
        en.writelines(new_sqlmap_urls)
        en.close()
        
            
        
