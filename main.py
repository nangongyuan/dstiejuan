import requests
from lxml import html
import MySQLdb
import threadpool
import os
import re

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
           "Host": "down.dstiejuan.com"}
main_url = "http://www.dstiejuan.com"

conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='',
        db='jianghuiyan',
        charset='utf8'
    )

task_pool = threadpool.ThreadPool(15)


def get_chapter_content(url):
    response = requests.get(url)
    reg = '<div id="content".*?>(.*?)</div>'
    content = re.findall(reg, response.text, re.S)[0]
    content = re.sub(r'<p>', '', content)
    content = re.sub(r'</p>', '\n', content)
    chapter_title = re.findall(r'<h1>(.*?)</h1>', response.text, re.S)[0]
    content = '\n' + chapter_title + '\n\n' + content
    return content


def list_chapter(url):
    response = requests.get(url)
    content = html.etree.HTML(response.text)
    name = content.xpath("//div[@class='headline']/h1/text()")[0]
    type = content.xpath("//div[@class='headline']/p/a/text()")[0]
    author = content.xpath("//div[@class='headline']/h2/a/text()")[0]
    chapter_url = content.xpath("//div[@class='read']/dl")[1].xpath("./dd/a/@href")
    if not os.path.exists("H:/jianghuiyan/"+type):
        os.mkdir("H:/jianghuiyan/"+type)
    file_name = f"H:/jianghuiyan/{type}/{name}_{author}.txt"
    print("打开文件："+file_name)
    fobj = open(file_name, 'a')
    for url in chapter_url:
        for i in range(1, 5):
            chapter_content = ''
            try:
                chapter_content = get_chapter_content(main_url + url)
                break
            except BaseException:
                continue
        fobj.write(chapter_content)
    fobj.close()

    cur = conn.cursor()
    sql = "insert into novel (name,type,author,download_url,remark) values (%s,%s,%s,%s,%s)"
    cur.execute(sql, (name, type, author, main_url + url, main_url))
    conn.commit()
    cur.close()


def get_story_info(url):
    response = requests.get(url)
    content = html.etree.HTML(response.text)
    download_url = content.xpath("//p[@class='action']/a")[0].xpath("./@href")[0]
    list_chapter(main_url+download_url)


def list_story(content):
    story_list = content.xpath("//table[@class='layui-table']/tbody/tr")
    url_list = []
    for story in story_list:
        a = story.xpath(".//a")
        url = main_url + a[1].xpath("./@href")[0]
        url_list.append(url)

    task_list = threadpool.makeRequests(get_story_info, url_list)
    [task_pool.putRequest(req) for req in task_list]
    task_pool.wait()


for page in range(1, 11):
    full_url = f"http://www.dstiejuan.com/full/{page}.html"
    response = requests.get(full_url)
    content = html.etree.HTML(response.text)
    list_story(content)
    print("一页爬完")

conn.close()
print("完成")
