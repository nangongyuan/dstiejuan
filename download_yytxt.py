from pathlib import Path
import requests
from lxml import html
import MySQLdb
import os
import threadpool
import zipfile
import threading
import time
import urllib3

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"}
main_url = "https://www.yytxt.com"



def get_conn():
    conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='',
            db='jianghuiyan',
            charset='utf8'
        )
    return conn


task_pool = threadpool.ThreadPool(5)

request = requests.session()
request.keep_alive = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_response(url):
    for i in range(1, 4):
        try:
            response = request.get(url, timeout=60, headers=headers, verify=False)
            return response
        except BaseException as e:
            print(e)
            print("获取"+url+"失败")


def get_novel(name, author):
    conn = get_conn()
    cur = conn.cursor()
    sql = "select name from novel where name=%s and author=%s"
    cur.execute(sql, (name, author))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return len(results) > 0


def save_novel(name, type, author, download_url, remark):
    print(name + "---" + author + "---" + type + "--- " + download_url)
    print("开始下载："+name)
    response = request.get(download_url, timeout=100, headers=headers, verify=False)
    if response.status_code != 200:
        print("下载失败 " + download_url)
        raise BaseException
    if not os.path.exists("d:/jianghuiyan/"+type):
        os.mkdir("d:/jianghuiyan/"+type)
    file_name = f"d:/jianghuiyan/{type}/{name}_{author}.txt"
    if os.path.exists(file_name):
        print("已存在"+file_name)
        return
    print("写文件："+file_name)
    with open(file_name, "wb") as file:
        file.write(response.content)

    print("写入数据库："+f"{name}_{type}_{author}_{download_url}")
    conn = get_conn()
    cur = conn.cursor()
    sql = "insert into novel (name,type,author,download_url,remark) values (%s,%s,%s,%s,%s)"
    cur.execute(sql, (name, type, author, download_url, remark))
    conn.commit()
    cur.close()
    conn.close()


def download_story(url, name, author, type):
    response = get_response(url)
    content = html.etree.HTML(response.text)
    if get_novel(name, author):
        print(name+"_"+author+"----已存在")
        return
    download_url = content.xpath("//div[@id='TxtdownTop']")[0].xpath("./a/@href")[1]
    for i in range(1, 4):
        try:
            save_novel(name, type, author, download_url, main_url)
            break
        except BaseException as e:
            print(e)


def get_story_info(url):
    response = get_response(url)
    content = html.etree.HTML(response.text)
    print(url)
    name = content.xpath("//div[@id='info']/h1/text()")[0]
    author = content.xpath("//div[@id='info']/p/text()")[0].split("：")[1]
    type = content.xpath("//div[@id='info']/p/text()")[1].split("：")[1]
    download_url = content.xpath("//div[@id='info']/p/a")[3].xpath("./@href")[0]
    download_story(download_url, name, author, type)


def list_story(content):
    story_list = content.xpath("//div[@class='novelslist']/ul/li")
    url_list = []
    for story in story_list:
        a = story.xpath("./span/a")
        url = a[0].xpath("./@href")[0]
        url_list.append(url)
    task_list = threadpool.makeRequests(get_story_info, url_list)
    [task_pool.putRequest(req) for req in task_list]
    task_pool.wait()


for page in range(1, 207):
    full_url = f"https://www.yytxt.com/daquan/0_0_0_0_2_0_0_0_{page}.html"
    response = get_response(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")


print("完成")
