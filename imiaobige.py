import requests
from lxml import html
import MySQLdb
import os
import threading
from time import sleep
from queue import Queue

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"}
main_url = "http://www.imiaobige.com"

conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='',
        db='jianghuiyan',
        charset='utf8'
    )


def save_novel(name, type, author, download_url, remark):
    print("开始下载："+name+"----"+download_url)
    response = requests.get(download_url)
    if not os.path.exists("H:/jianghuiyan/"+type):
        os.mkdir("H:/jianghuiyan/"+type)
    file_name = f"H:/jianghuiyan/{type}/{name}_author:{author}.txt"
    print("写文件："+file_name)
    print(response.content)
    with open(file_name, "wb") as file:
        file.write(response.content)

    print("写入数据库："+f"{name}_{type}_{author}_{download_url}")
    cur = conn.cursor()
    sql = "insert into novel (name,type,author,download_url,remark) values (%s,%s,%s,%s,%s)"
    cur.execute(sql, (name, type, author, download_url, remark))
    conn.commit()
    cur.close()


def download_story(url):
    response = requests.get(url)
    content = html.etree.HTML(response.text)
    detail = content.xpath("//div[@class='booktitle']")[0]
    name = detail.xpath("//h1/text()")[0]
    author = detail.xpath("//span[@id='author']/a/text()")[0]
    type = content.xpath("//div[@class='count']//li/span/text()")[0]
    download_url = content.xpath("//li[@class='downlink']")[1].xpath("./a/@href")[0]
    save_novel(name, type, author, download_url, main_url)


def get_story_info(url):
    response = requests.get(url, headers=headers)
    content = html.etree.HTML(response.text)
    download_url = content.xpath("//div[@class='motion']/a")[1].xpath("./@href")[0]
    download_story(main_url+download_url)


def list_story(content):
    story_list = content.xpath("//table[@class='booklists']/tbody/tr")
    count = 0
    threads = []
    for story in story_list:
        a = story.xpath(".//a")[0]
        url = main_url + a.xpath("./@href")[0]
        get_story_info(url)
    #     t = threading.Thread(target=get_story_info, args=(url, ))
    #     threads.append(t)
    #     t.start()
    #     count = count + 1
    #     if(count%5 == 0):
    #         sleep(1)
    # for thread in threads:
    #     thread.join()


for page in range(1, 2):
    full_url = f"http://www.imiaobige.com/shuku/0_0_2_{page}.html"
    response = requests.get(full_url, headers=headers)
    content = html.etree.HTML(response.text)
    list_story(content)
    sleep(60)
    print("一页爬完")

conn.close()
print("完成")
