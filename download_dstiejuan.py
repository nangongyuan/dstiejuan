import requests
from lxml import html
import MySQLdb
import os
import threadpool

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"}
main_url = "http://www.dstiejuan.com"

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


def save_novel(name, type, author, download_url, remark):
    response = requests.get(download_url)
    if response.status_code != 200:
        raise BaseException
    if not os.path.exists("f:/jianghuiyan/"+type):
        os.mkdir("f:/jianghuiyan/"+type)
    file_name = f"f:/jianghuiyan/{type}/{name}_{author}.txt"
    print("写文件："+file_name)
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
    detail = content.xpath("//div[@class='detail']")[0]
    name = detail.xpath("//h1/text()")[0]
    author = detail.xpath("./p/a/text()")[0]
    if get_novel(name, author):
        print(name+"_"+author+"----已存在")
        return
    type = detail.xpath("./p/a/text()")[1]
    download_url = content.xpath("//ul[@class='list bg']")[0].xpath("./li/a/@href")[1]
    save_novel(name, type, author, download_url, main_url)


def get_story_info(url):
    response = requests.get(url, headers=headers)
    content = html.etree.HTML(response.text)
    download_url = content.xpath("//p[@class='action']/a")[1].xpath("./@href")[0]
    for i in range(1, 4):
        try:
            download_story(main_url + download_url)
            break
        except BaseException as e:
            print(e)



def list_story(content):
    story_list = content.xpath("//table[@class='layui-table']/tbody/tr")
    url_list = []
    for story in story_list:
        a = story.xpath(".//a")
        url = main_url + a[1].xpath("./@href")[0]
        url_list.append(url)
    task_list = threadpool.makeRequests(get_story_info, url_list)
    [task_pool.putRequest(req) for req in task_list]


for i in range(1,11):
    for page in range(1, 11):
        full_url = f"http://www.dstiejuan.com/full/{page}.html"
        response = requests.get(full_url)
        content = html.etree.HTML(response.text)
        list_story(content)
        print(f"第{page}页爬完")

task_pool.wait()

conn.close()
print("完成")
