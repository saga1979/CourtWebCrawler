import requests  
from bs4 import BeautifulSoup  
from pymongo import MongoClient
from dateutil import parser

connection_string = "mongodb://localhost:27017"

client = MongoClient(connection_string)

db = client["scfroot"]
collection = db["cases.directive"]
#先删除集合内的数据
collection.drop()
  
# 目标网页的URL  
url = 'https://www.court.gov.cn/shenpan/gengduo/77.html'  
  
# 发送HTTP请求获取网页内容  
response = requests.get(url)  
  
# 使用BeautifulSoup解析网页内容  
soup = BeautifulSoup(response.text, 'html.parser')  
  
# 提取所需的信息，这里以提取所有段落标签为例  
#paragraphs = soup.find_all('div', {"class":"txt_txt", })  

sec_list = soup.find('div' , {"class": "sec_list"})
sec_list = sec_list.find('ul' )
secs = sec_list.find_all("li")
  
# 打印所有段落的内容 
url_pre = "https://www.court.gov.cn" 
case_url_list = []
for sec in secs: 
   
    #print(sec.get_text(), sec.a['href'])
    case_url_list.append(sec.a['href'])

# 获取所有案例内容
case_content={}
translation_table = str.maketrans("", "", "\xa0")
for case_url in case_url_list:
 
    response = requests.get(url_pre + case_url)  
    soup = BeautifulSoup(response.text, 'html.parser')  
    content = soup.find("div", {"class":"detail"})
    
    publish = content.find("ul", {"class":"clearfix fl message"}).find("li", {"class":"fl"}, string=lambda text: "发布时间" in text)
    case_content["PublishTime"] = parser.parse(publish.get_text()[5:])
    case = content.find("div", {"class":"txt_txt"})
    case_content["Number"] = case.find("strong", string=lambda text : "指导" in text).text.strip()
    #case_content["Title"] = case.find("strong", string=lambda text : "指导" not in text).text.strip()
    title = content.find("div", {"class": "title"}).text.strip()
    title = title[title.index("号")+2:]
    case_content["Title"] = title
    case_content["Keywords"] = case.find("strong" , string= lambda text : "关键词" in text).parent.text.translate(translation_table).strip().removeprefix("关键词").strip()
    case_content["Url"] = url_pre + case_url
    case_content["Content"] = case.text.strip("\n")
    response.close()
    print(case_content)
    collection.insert_one(case_content)
    break


client.close()



