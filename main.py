import requests
from bs4 import BeautifulSoup
import os
import re


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
    new_title = re.sub(rstr, "__", title)
    return new_title


def getHTMLText(url, code="utf-8", timeout=30):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        r.encoding = code
        soup = BeautifulSoup(r.text, 'lxml')
        return soup
    except Exception as e:
        print('Error while getting html text: ', e)
        return ""


def writeToFile(text, dirPath, filename):
    filePath = os.path.join(dirPath, filename+'.txt')
    with open(filePath, 'a') as file:
        file.write(text)


def getBookInfo(url):
    infoDict = {}
    circleListStr = ''
    staffList = []
    html = getHTMLText(url)
    mainTable = html.find('table', class_='mainborder')
    trList = mainTable.find_all('tr')
    for i in range(1, 12):
        kv = trList[i].find_all('td')
        key = kv[0].get_text()
        value = kv[1].get_text()
        infoDict[key] = value
    circleListStr = ','.join(i.get_text() for i in mainTable.find_all('a', href=re.compile(r'circle')) if i.get_text())
    staffList = [i.get_text() for i in mainTable.find_all('a', href=re.compile(r'author')) if i.get_text()]
    cover = html.find('img', alt='cover')
    coverSrc = cover['src'] if cover else ''
    formResult(infoDict, circleListStr, staffList, coverSrc)


def getCircleAll(url):
    html = getHTMLText(url)
    circleName = html.find('div', id='page_name').get_text().replace('Circles:', '').strip()
    global path
    path = os.path.join(path, validateTitle(circleName))
    if not os.path.exists(path):
        os.mkdir(path)
    while True:
        html = getHTMLText(url)
        bookListHTML = html.find_all('div', class_='bookinfo')
        if not bookListHTML:
            break
        for each in bookListHTML:
            if each.find(string='Touhou Project'):
                getBookInfo("https://www.doujinshi.org"+each.find_parent().find('a').get('href'))

        url = html.find(class_='next', string='►')
        if url:
            url = "https://www.doujinshi.org" + url['href']
        else:
            break


def formResult(infoDict, circleListStr, staffList, coverSrc=None):
    title = infoDict['Original title:']
    staff = '\n'.join('*[['+eachStaff+']]' for eachStaff in staffList)
    result = f'''{{{{同人志头部}}}}

== 作品信息 ==
{{{{同人志信息|
| 封面 = {{{{PAGENAME}}}}封面.jpg
| 封面角色 =
| 名称 = {title}
| 译名 =
| 制作方 = {circleListStr}
| 类型 = 漫画
| 展会 = {infoDict['Convention:'].strip()}
| 年龄限制 = {'R18' if infoDict['Adult:']=='Yes' else '一般向'}
| 尺寸 = B5
| 页数 = {infoDict['Pages:']}
| 编号 =
| 登场人物 =
| 售价 =
| 官网页面 =
|
}}}}

== Staff ==
{staff}

== 评论 ==

{{{{Bottom}}}}'''

    fileTitle = validateTitle(title)
    writeToFile(result, path, infoDict['Released:']+'__'+fileTitle)
    print(title)
    saveCover(path, fileTitle, infoDict['Released:'], coverSrc)  # comment out this line to disable save doujinshi cover


def saveCover(path, title, releaseDate, coverSrc=None, timeout=30):
    if coverSrc:
        try:
            imgContent = requests.get('https:' + coverSrc, timeout=timeout).content
            if imgContent:
                with open(os.path.join(path, f'{releaseDate}__{title}.jpg'), 'wb') as imgFile:
                    imgFile.write(imgContent)
        except Exception as e:
            print('Error while saving cover: ', e)
        #print(coverSrc)


path=os.path.abspath('.')
#getBookInfo("https://www.doujinshi.org/book/17221/")
#getCircleAll("https://www.doujinshi.org/browse/circle/1974/")

url = input("circle page 's url:")
getCircleAll(url)
