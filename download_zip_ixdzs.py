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

# try:
#     file_zip = zipfile.ZipFile(file_name, 'r')
#     for file in file_zip.namelist():
#         extracted_path = Path(file_zip.extract(file, 'h:/jianghuiyan/' + type + '/'))
#         extracted_path.rename('h:/jianghuiyan/' + type + '/' + name + "_" + author + ".txt")
#     file_zip.close()
#     os.remove(file_name)
# except BaseException as e:
#     print(e)
#     os.remove(file_name)

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"}
main_url = "https://www.ixdzs.com"



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


task_pool = threadpool.ThreadPool(15)

request = requests.session()
request.keep_alive = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_response(url):
    for i in range(1, 4):
        try:
            response = request.get(url, timeout=10, verify=False)
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
    print("开始下载："+name)
    response = request.get(download_url, timeout=10, verify=False)
    if response.status_code != 200:
        print("下载失败")
        raise BaseException
    if not os.path.exists("e:/jianghuiyan/"+type):
        os.mkdir("e:/jianghuiyan/"+type)
    file_name = f"e:/jianghuiyan/{type}/{name}_{author}.zip"
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


def download_story(url):
    response = get_response(url)
    content = html.etree.HTML(response.content.decode("utf-8"))
    name = content.xpath('//meta[@property="og:novel:book_name"]/@content')[0]
    author = content.xpath('//meta[@property="og:novel:author"]/@content')[0]
    if get_novel(name, author):
        print(name+"_"+author+"----已存在")
        return
    type = content.xpath('//meta[@property="og:novel:category"]/@content')[0]
    type = type.replace('·', '')

    download_url = main_url + content.xpath("//div[@id='txt_down']")[0].xpath("./a/@href")[0]
    for i in range(1, 4):
        try:
            save_novel(name, type, author, download_url, main_url)
            break
        except BaseException as e:
            print(e)


def list_story(content):
    story_list = content.xpath("//span[@class='b_t']")
    url_list = []
    for story in story_list:
        a = story.xpath("./a")
        url = main_url + a[0].xpath("./@href")[0]
        url_list.append(url)
    task_list = threadpool.makeRequests(download_story, url_list)
    [task_pool.putRequest(req) for req in task_list]
    task_pool.wait()


# for page in range(1, 250):
#     full_url = f"https://www.ixdzs.com/sort/1/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")


# for page in range(1, 67):
#     full_url = f"https://www.ixdzs.com/sort/0/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")


# for page in range(1, 60):
#     full_url = f"https://www.ixdzs.com/sort/2/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")


# for page in range(1, 200):
#     full_url = f"https://www.ixdzs.com/sort/3/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")



for page in range(1, 36):
    full_url = f"https://www.ixdzs.com/sort/4/index_0_2_0_{page}.html"
    response = get_response(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")


#
# for page in range(1, 52):
#     full_url = f"https://www.ixdzs.com/sort/5/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 98):
#     full_url = f"https://www.ixdzs.com/sort/6/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 317):
#     full_url = f"https://www.ixdzs.com/sort/7/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 29):
#     full_url = f"https://www.ixdzs.com/sort/8/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 999):
#     full_url = f"https://www.ixdzs.com/sort/9/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 69):
#     full_url = f"https://www.ixdzs.com/sort/10/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 6):
#     full_url = f"https://www.ixdzs.com/sort/11/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 40):
#     full_url = f"https://www.ixdzs.com/sort/12/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 34):
#     full_url = f"https://www.ixdzs.com/sort/13/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 63):
#     full_url = f"https://www.ixdzs.com/sort/14/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()
#
# for page in range(1, 3):
#     full_url = f"https://www.ixdzs.com/sort/15/index_0_2_0_{page}.html"
#     response = get_response(full_url)
#     content = html.etree.HTML(response.text)
#     list_story(content)
#     print(f"第{page}页爬完")
#
# task_pool.wait()


print("完成")
