#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 @File       : instagram_user.py
 @Time       : 2018/6/3 0012 21:22
 @Author     : SomeZ
 @Contact    : tzaliyun@163.com
 @Description:...
 @statesment: Basic Empty Chan
"""
import re
import json
import os
from lxml import etree
import requests
import click
from urllib import parse
import time
import random
from multiprocessing import Pool, Lock 
#from hashlib import md5
#import urllib.request
#from http import cookiejar
#import urllib.response


headers = {
    "Origin": "https://www.instagram.com/",
    "Referer": "https://www.instagram.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Host": "www.instagram.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, sdch",
    "accept-language": "zh-CN,zh;q=0.8",
    "X-Instragram-AJAX": "1",
    "X-Requested-With": "XMLHttpRequest",
    "Upgrade-Insecure-Requests": "1",  
}
HEADER = {
    #"Referer": temp_url,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }

jso = {"id": "", "first": 12, "after": ""}

BASE_URL = "https://www.instagram.com/"
NEXT_URL = 'https://www.instagram.com/graphql/query/?query_hash=42323d64886122307be10013ad2dcc44&variables={0}'

new_imgs_url = []


def crawl(query):
    folder = query.replace('.', '_')
    os.mkdir(folder)
    os.chdir(folder)
    people_url = BASE_URL + query + r'/'
    ins_session = requests.Session()
    response = ins_session.get(people_url, headers=headers)
    print(response.status_code)
    html = etree.HTML(response.text)
    
    all_a_tags = html.xpath('//script[@type="text/javascript"]/text()')
    try:
        for a_tag in all_a_tags:
            if a_tag.strip().startswith('window'):
                data = a_tag.split('= {')[1][:-1]
                js_data = json.loads('{' + data, encoding='utf-8')
                id_ = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
                edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
                click.echo(id_)
                end_cursor = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
                click.echo(end_cursor)
                has_next = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                click.echo(has_next)
                for edge in edges:
                    click.echo(edge["node"]["display_url"])
                    #pool.apply(download(edge["node"]["display_url"]))
                    new_imgs_url.append(edge["node"]["display_url"])
    except IndexError:
        pass
    next_crawl(id_, has_next, end_cursor)

def next_crawl(userID, is_next, after_token):
    if bool(is_next):
        jso["id"] = userID
        jso["first"] = 12
        jso["after"] = after_token
        text = json.dumps(jso)
        url = NEXT_URL.format(parse.quote(text))
        print(url)
        next_response = requests.get(url, headers=headers)
        print(next_response.status_code)

        has_next = next_response.json()["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
        end_cursor = next_response.json()["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        edges = next_response.json()["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
        for edge in edges:
            click.echo(edge["node"]["display_url"])
            #pool.apply(download(edge["node"]["display_url"]))
            new_imgs_url.append(edge["node"]["display_url"])
        next_crawl(userID, has_next, end_cursor)

def download(img_url):
    lock = Lock()
    PIC_SESSION = requests.Session()
    img_res = PIC_SESSION.get(img_url, headers=HEADER)
    lock.acquire()
    ImgName = img_res.url.split('/')[-1]
    click.echo(img_res.cookies.items())
    click.echo(img_res.headers)
    with open(ImgName, 'wb') as f:
        f.write(img_res.content)
    lock.release()
    
if __name__ == '__main__':
    PeopleName = input('Please Input InsER：')
    crawl(PeopleName)
    pool = Pool()
    pool.map(download, new_imgs_url)


