import requests
import urllib
from bs4 import BeautifulSoup
import os
import re

def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
    new_title = re.sub(rstr, "__", title)
    return new_title

def getHTMLText(url,code="utf-8",timeout=30):
    try:
        r=requests.get(url)
        r.raise_for_status()
        r.encoding=code
        soup=BeautifulSoup(r.text,'html.parser')
        return soup
    except:
        return ""

def writeToFile(text,dirPath,filename):
    file=open(dirPath+filename+'.txt','a')
    file.write(text)
    file.close()

def getBookInfo(url):
    infoDict={}
    circleList=''
    staffList=[]
    html=getHTMLText(url)
    mainTable=html.find('table',attrs={'class':'mainborder'})
    trList=mainTable.find_all('tr')
    for i in range(1,12):
        kv=trList[i].find_all('td')
        key=kv[0].get_text()
        value=kv[1].get_text()
        infoDict[key]=value
    point=mainTable.find('div',string='Circles:').find_parent().find_parent()
    while True:
        point=point.find_next_sibling()
        if(point.find('div',string='Authors:')==None):
            circleList=circleList+point.find('td').find_next_sibling().get_text()+'，'
        else:
            break
    circleList=circleList[:-1]
    point=mainTable.find('div',string='Authors:').find_parent().find_parent()
    while True:
        point=point.find_next_sibling()
        if(point.find('div',string='Parodies:')==None):
            staffList.append(point.find('td').find_next_sibling().get_text())
        else:
            break
    cover=html.findAll('img',alt='cover')
    if(cover!=None):
        coverSrc=cover[0].get('src')
    formResult(infoDict,circleList,staffList,coverSrc)

def getCircleAll(url):
    html=getHTMLText(url)
    circleName=html.find('div',attrs={'id':'page_name'}).get_text().strip().replace('Circles: ','')
    global path
    path=path+validateTitle(circleName)+'/'
    if not os.path.exists(path):
        os.mkdir(path)
    page=0
    while True:
        page=page+1
        html=getHTMLText(url+'?page='+str(page))
        bookListHTML=html.find_all('div',attrs={'class':'bookinfo'})
        if bookListHTML==[]:
            break;
        for each in bookListHTML:
            if each.find(string='Touhou Project')!=None:
                getBookInfo("https://www.doujinshi.org"+each.find_parent().find('a').get('href'))

def formResult(infoDict,circleList,staffList,coverSrc=None):
    result="{{同人志头部}}\n\n== 作品信息 ==\n{{同人志信息|\n| 封面 = {{PAGENAME}}封面.jpg\n| 封面角色 = \n| 名称 = [ORIGINALTITLE]\n| 译名 = \n| 制作方 = [CIRCLES]\n| 类型 = [TYPE]\n| 展会 = [CONVENTION]\n| 年龄限制 = [AGELIMIT]\n| 尺寸 = [SCALE]\n| 页数 = [PAGES]\n| 编号 = \n| 登场人物 = \n| 售价 = \n| 官网页面 = \n|\n}}\n\n== Staff ==\n[STAFF]\n== 评论 ==\n\n{{Bottom}}"
    title=infoDict['Original title:']
    result=result.replace('[ORIGINALTITLE]',title)
    result=result.replace('[CIRCLES]',circleList)
    result=result.replace('[TYPE]','漫画')
    result=result.replace('[CONVENTION]',infoDict['Convention:'].strip())
    if(infoDict['Adult:']=='Yes'):
        result=result.replace('[AGELIMIT]','R18')
    else:
        result=result.replace('[AGELIMIT]','一般向')
    result=result.replace('[SCALE]','B5')
    result=result.replace('[PAGES]',infoDict['Pages:'])
    staff=''
    for eachStaff in staffList:
        staff=staff+'*[['+eachStaff+']]\n'
    result=result.replace('[STAFF]',staff)
    writeToFile(result,path,infoDict['Released:']+'__'+validateTitle(title))
    print(title)
    saveCover(path,title,coverSrc)#comment out this line to disable save doujinshi cover

def saveCover(path,title,coverSrc=None):
    if(coverSrc!=None):
        #print(coverSrc)
        urllib.request.urlretrieve('https:'+coverSrc,"%s%s封面.jpg"%(path,validateTitle(title)))
        
path='./'
#getBookInfo("https://www.doujinshi.org/book/17221/")
#getCircleAll("https://www.doujinshi.org/browse/circle/1974/")

url=input("circle page 's url:")
getCircleAll(url)