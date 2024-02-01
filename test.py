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
case_list_url_pre = 'https://www.court.gov.cn/shenpan/gengduo/'  
case_url_pre = "https://www.court.gov.cn" 
# 找到所有的案例列表
pages = 1
case_url_bads = []
case_url_list = []
while True:
    
    pages_str = "77"  if pages==1 else ("77_" + str(pages))
    url = case_list_url_pre + pages_str + ".html"
    
    # 发送HTTP请求获取网页内容  
    response = requests.get(url)  
    if  not response.ok:
        print("无法请求：" , url)
        break

    # 发送HTTP请求获取网页内容  
    response = requests.get(url)    
    # 使用BeautifulSoup解析网页内容  
    soup = BeautifulSoup(response.text, 'html5lib')  
    sec_list = soup.find('div' , {"class": "sec_list"})
    sec_list = sec_list.find('ul' )
    secs = sec_list.find_all("li")    
    # 打印所有段落的内容 
    for sec in secs:    
        #print(sec.get_text(), sec.a['href'])
        if "号"  not in sec.a["title"] :
            continue
        case_url_list.append(case_url_pre + sec.a['href'])
        print(sec.a["title"].strip()+":")
        
        print( sec.a['href'])

    pages+=1
    #测试用，只解析一个页面
    #break

translation_table = str.maketrans("", "", "\xa0")
for case_url in case_url_list:
    # 发送HTTP请求获取网页内容 
    case_content = {} 
    try:
        response = requests.get(case_url)

        soup = BeautifulSoup(response.text, 'html5lib') 
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
        case_content["Url"] =  case_url
        case_content["Content"] = str(case)
        response.close()
        # print(case_content["Content"])
        collection.insert_one(case_content)
    except Exception as e:
        print(case_url, ":", e)
        case_url_bads.append(case_url)
        break 
client.close()

print("bad url:", case_url_bads)



