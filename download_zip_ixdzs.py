from pathlib import Path
import requests
from lxml import html
import MySQLdb
import os
import threadpool
import zipfile
import threading

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"}
main_url = "https://www.ixdzs.com"

conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='',
        db='jianghuiyan',
        charset='utf8'
    )

task_pool = threadpool.ThreadPool(20)


def get_novel(name, author):
    cur = conn.cursor()
    sql = "select name from novel where name=%s and author=%s"
    cur.execute(sql, (name, author))
    results = cur.fetchall()
    cur.close()
    return len(results) > 0


thread_lock = threading.Lock()


def save_novel(name, type, author, download_url, remark):
    global thread_lock
    print("开始下载："+name)
    response = requests.get(download_url, timeout=10)
    if response.status_code != 200:
        print("下载失败")
        raise BaseException
    if not os.path.exists("h:/jianghuiyan/"+type):
        os.mkdir("h:/jianghuiyan/"+type)
    if os.path.exists('h:/jianghuiyan/'+type+'/'+name+"_"+author+".txt"):
        return
    file_name = f"h:/jianghuiyan/{type}/{name}_{author}.zip"
    print("写文件："+file_name)
    try:
        thread_lock.acquire()
        with open(file_name, "wb") as file:
            file.write(response.content)
        file_zip = zipfile.ZipFile(file_name, 'r')
        for file in file_zip.namelist():
            extracted_path = Path(file_zip.extract(file, 'h:/jianghuiyan/'+type+'/'))
            extracted_path.rename('h:/jianghuiyan/'+type+'/'+name+"_"+author+".txt")
        file_zip.close()
        os.remove(file_name)
    except BaseException as e:
        print(e)
        return
    finally:
        thread_lock.release()
    print("写入数据库："+f"{name}_{type}_{author}_{download_url}")
    cur = conn.cursor()
    sql = "insert into novel (name,type,author,download_url,remark) values (%s,%s,%s,%s,%s)"
    cur.execute(sql, (name, type, author, download_url, remark))
    conn.commit()
    cur.close()


def download_story(url):
    response = requests.get(url)
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


for page in range(1, 250):
    full_url = f"https://www.ixdzs.com/sort/1/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 67):
    full_url = f"https://www.ixdzs.com/sort/0/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 60):
    full_url = f"https://www.ixdzs.com/sort/2/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()


for page in range(1, 200):
    full_url = f"https://www.ixdzs.com/sort/3/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 36):
    full_url = f"https://www.ixdzs.com/sort/4/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 52):
    full_url = f"https://www.ixdzs.com/sort/5/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 98):
    full_url = f"https://www.ixdzs.com/sort/6/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 317):
    full_url = f"https://www.ixdzs.com/sort/7/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 29):
    full_url = f"https://www.ixdzs.com/sort/8/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 999):
    full_url = f"https://www.ixdzs.com/sort/9/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 69):
    full_url = f"https://www.ixdzs.com/sort/10/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 6):
    full_url = f"https://www.ixdzs.com/sort/11/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 40):
    full_url = f"https://www.ixdzs.com/sort/12/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 34):
    full_url = f"https://www.ixdzs.com/sort/13/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 63):
    full_url = f"https://www.ixdzs.com/sort/14/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

for page in range(1, 3):
    full_url = f"https://www.ixdzs.com/sort/15/index_0_2_0_{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print(f"第{page}页爬完")

task_pool.wait()

conn.close()
print("完成")