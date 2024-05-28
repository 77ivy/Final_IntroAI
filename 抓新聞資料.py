from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime, timedelta
import requests
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

NewsTypeDict={
  "ETtoday": "&KEY_WORD=&NEWS_SRC=ETtoday%E6%96%B0%E8%81%9E%E9%9B%B2",
  "Self": "&KEY_WORD=&NEWS_SRC=%E5%85%AC%E5%91%8A%E8%A8%8A%E6%81%AF",
  "Anue": "&KEY_WORD=&NEWS_SRC=Anue%E9%89%85%E4%BA%A8"
  }

def getSelfNews(driver, newsLinkList):
  # 初始化 WebDriver
  newsList=[]
  for date, url in newsLinkList:
    driver.get(url)
    try:
      Info = driver.find_element(By.CSS_SELECTOR, 'td[bgcolor="white"][colspan="6"][style="padding:16px 9px 16px 18px;font-size:11pt;line-height:28px;"]')
      newsList.append((date,Info.text.replace("\n","")))
    except:
      continue
  return newsList

def getAnueNews(newsLinkList):
  newsList=[]
  for date, url in newsLinkList:
    content=""
    response = requests.get(url)
    if response.status_code == 200:
      soup = BeautifulSoup(response.content, 'html.parser')
      # 查找主新聞區域的元素
      main_article = soup.find('main', id='article-container')
      if main_article:
        title = soup.find('h1').get_text(strip=True)
        paragraphs = main_article.find_all('p')
        content = ''.join([para.get_text(strip=True) for para in paragraphs])
        newsList.append((date, content))
      else:
        continue
  return newsList

def getETtodayNews(driver, newsLinkList):
  newsList=[]
  # 初始化 WebDriver
  for date, url in newsLinkList:
    article_text=""
    driver.get(url)
    try:
      page_content = driver.page_source
      soup = BeautifulSoup(page_content, 'html.parser')
      article_content = soup.find('div', class_='story')
      # 提取文章内文
      if article_content:
        paragraphs = article_content.find_all('p', class_=lambda x: x != 'ai_notice')
        article_text = "".join([paragraph.get_text(strip=True) for paragraph in paragraphs[3:]])
      newsList.append((date,article_text))
    except:
      continue
  return newsList



"""
輸入日期計算一年前日期
日期格式: "年-月-日"
ex: 2024-5-24
"""
def twoWeeksBefore(date_str):
  date = datetime.strptime(date_str, "%Y-%m-%d")
  two_weeks_ago = date - timedelta(days=0)
  return two_weeks_ago.strftime("%Y-%m-%d")


'''
用來提取股票某個日期前一年的新聞連結
input:
date: 輸入想要提取新聞的日期
stockId: 輸入想要的股票代碼
lastType: 想找什麼類別的新聞

return:
一個列表每個元素裡面有兩個子元素
first element : 這篇新聞的日期
second element : 這篇新聞的連結
'''
def getNewsLinkTwoWeeks(driver, endDate, stockId, lastType):
  #紀錄網址
  startDate=twoWeeksBefore(endDate)
  front="https://goodinfo.tw/tw/StockAnnounceList.asp?"
  middle=f"PAGE=1&START_DT={startDate}&END_DT={endDate}&STOCK_ID={stockId}"
  url = front+middle+NewsTypeDict[lastType]
  # 打開網頁
  driver.get(url)
  time.sleep(random.uniform(5, 12))
  #獲取新聞總共有幾頁
  pageInfo = driver.find_element(By.CSS_SELECTOR, "td[style='text-align:right;color:gray;font-size:9pt;']")
  pageInfo = pageInfo.text.strip()
  totalPages = re.search(r'\共(\d+)頁', pageInfo)
  pageNum=int(totalPages.group(1))+1
  newsLinkList=[]
  #從第一頁開始獲取新聞的連結
  for pageNumber in range(1,pageNum):
    middle=f"PAGE={pageNumber}&START_DT={startDate}&END_DT={endDate}&STOCK_ID={stockId}"
    url = front+middle+NewsTypeDict[lastType]
    driver.get(url)
    time.sleep(random.uniform(5, 12))
    tableInfos= driver.find_elements(By.CSS_SELECTOR, "td[style='word-break:break-all;padding:8px 4px;']")
    for table in tableInfos:
      linkInfo= table.find_element(By.CLASS_NAME,'link_black')
      newsLink= linkInfo.get_attribute("href")

      dateInfo= table.find_element(By.CSS_SELECTOR,"span[style='font-size:9pt;color:gray;font-weight:normal;']")
      dateList=dateInfo.text.split()
      date=dateList[1]

      newsLinkList.append((date, newsLink))
  return newsLinkList

'''
用來提取股票某個日期前一年的新聞
input:
date: 輸入想要提取新聞的日期
stockId: 輸入想要的股票代碼

return:
一個列表每個元素裡面有兩個子元素
first element : 這篇新聞的日期
second element : 這篇新聞

輸入範例:
getNews(driver, "2022-05-24", 2330)
'''
def getNews(driver, endDate, stockId):
  LinkList1=getNewsLinkTwoWeeks(driver, endDate, stockId, "ETtoday")
  LinkList1=list(dict.fromkeys(LinkList1))
  newList1=getETtodayNews(driver, LinkList1)

  LinkList2=getNewsLinkTwoWeeks(driver, endDate, stockId, "Anue")
  LinkList2=list(dict.fromkeys(LinkList2))
  newList2=getAnueNews(LinkList2)

  LinkList3=getNewsLinkTwoWeeks(driver, endDate, stockId, "Self")
  LinkList3=list(dict.fromkeys(LinkList3))
  newList3=getSelfNews(driver, LinkList3)

  allNewsList=newList1+newList2+newList3

  return allNewsList
def generate_dates_list():
  today = datetime.today()
  end_date = today - timedelta(days=365*5)  
  delta = timedelta(days=1)
  
  dates_list = []
  current_date = today
  while current_date >= end_date:
    dates_list.append(current_date.strftime("%Y-%m-%d"))
    current_date -= delta
  return dates_list
def save(stockId):
  dates_list_dt = generate_dates_list()
  r=dates_list_dt.index("2024-09-14")
  #a=dates_list_dt.index("2023-09-15")
  for date in dates_list_dt[r:]:
    try:
        filename=f"{date}News.txt"
        newsList=getNews(driver, date, stockId)
        News=[x[1] for x in newsList]
        with open(filename, 'w',encoding='UTF-8') as file:
          #file.write(date + '\n')
            for news in News:
                file.write(news + '\n')
    except:
        print(date)
        continue

'''
使用前記得先
pip install selenium
然後做以下設置
之後的parameter裡面的driver都用這個設好的去跑
拿新聞就用getNews就好其他都是副程式
'''


# 隨機選擇代理
# 設置 WebDriver

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# 初始化 WebDriver
driver = webdriver.Chrome(options=options)
#NewList= getNews(driver, "2022-05-24", 2330)
save(2330)
