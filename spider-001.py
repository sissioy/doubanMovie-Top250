# coding = utf-8
# @Time : 2020-01-19
# @Author : Sissioy
# @File : spider-001.py
# @Software : VS Code

import re
from bs4 import BeautifulSoup
import urllib.request, urllib.error
import xlwt
import sqlite3


def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 1.爬取数据
    datalist = getData(baseurl)
    # 3.保存数据
    # savepath = ".\\doubanMoviesTop250.xls"

    # saveData(datalist, savepath)
    dbpath = "doubanMoviesTop250.db"
    saveDataDB(datalist, dbpath)


# 影片详情
findlink = re.compile(r'<a href="(.*?)">')  # 生成创建正则表达式对象，表示规则（字符串模式）
# 影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S 让换行符包含在里面
# 影片片名
findTitle = re.compile(r'<span class="title">(.*?)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 找到评价人数
findJudge = re.compile(r"<span>(\d*)人评价</span>")
# 找到概况
findInq = re.compile(r'<span class="inq">(.*?)</span>')
# 找到影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 1.爬取数据
def getData(baseurl):
    datalist = []

    for i in range(0, 10):  # 调用获取页面信息的数据10次
        url = baseurl + str(i * 25)
        html = askURL(url)  # 保存html源码

        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):
            # print(item)  # 测试查看电影item
            data = []  # 保存一部电影的所有信息
            item = str(item)

            # 2. 标签解析&正则提取
            link = re.findall(findlink, item)[0]  # re库通过正则表达式找到指定字符串
            data.append(link)
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)
            titles = re.findall(findTitle, item)
            if len(titles) == 2:
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace("/", "")
                data.append(otitle)

            else:
                # print(titles)
                data.append(titles[0])
                data.append(" ")  # 外国名留空

            rating = re.findall(findRating, item)[0]
            data.append(rating)
            judge = re.findall(findJudge, item)[0]
            data.append(judge)
            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")
                data.append(inq)
            else:
                data.append("  ")

            bd = re.findall(findBd, item)[0]
            bd = re.sub("<br(\s+)?/>(\s+)?", " ", bd)
            bd = re.sub("/", " ", bd)
            data.append(bd.strip())

            datalist.append(data)

    return datalist


# 3.保存数据
def saveData(datalist, savepath):
    print("save...")
    workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook
    worksheet = workbook.add_sheet("豆瓣电影Top250", cell_overwrite_ok=True)  # 创建工作表
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外文名", "评分", "评价数", "概况", "相关信息")

    for i in range(0, 8):  # 保存列名
        worksheet.write(0, i, col[i])

    for i in range(0, 250):  # 保存数据
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 8):
            worksheet.write(i + 1, j, data[j])

    workbook.save(savepath)


def saveDataDB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 5 or index == 4:
                continue
            data[index] = '"' + data[index] + '"'
        c.execute(
            """
        INSERT INTO movie250 (
            info_link,pic_link,cname,ename,score,rated,introduction,info
        )
        VALUES (%s)
        """
            % ",".join(data)
        )
        conn.commit()
    c.close()
    conn.close()


def init_db(dbpath):
    sql = """
    CREATE TABLE movie250
    (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        introduction text,
        info text
    )
    """
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()


# 得到一个指定url的网页内容
def askURL(url):
    head = {}
    head[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    # 用户代理是伪装用的，告诉豆瓣服务器要什么信息
    # 模拟头部

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    return html


if __name__ == "__main__":
    # askURL("https://movie.douban.com/top250?start=")
    main()
    # init_db("movie_test.db")

    print("爬取完毕！")