import requests  
from bs4 import BeautifulSoup  
from pymongo import MongoClient
from dateutil import parser



def CaseListFetch(max=100):
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
            case_url_bads.append(url)
            continue
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
        if pages >= max:
            break
    return case_url_list, case_url_bads


translation_table = str.maketrans("", "", "\xa0")

def CaseParser(case_url):
    case_info = {}
    #try:
    response = requests.get(case_url)

    soup = BeautifulSoup(response.text, 'html5lib') 
    detail_content = soup.find("div", {"class":"detail"})        
    publish_time = detail_content.find("ul", {"class":"clearfix fl message"}).find("li", {"class":"fl"}, string=lambda text: "发布时间" in text)
    case_info["PublishTime"] = parser.parse(publish_time.get_text()[5:])
    case = detail_content.find("div", {"class":"txt_txt"})
    #case_content["Number"] = case.find("strong", string=lambda text : "指导" in text).text.strip()
    title_tag = detail_content.find("div", class_="title")
    case_info["Number"] = int( title_tag.text[title_tag.text.index("例")+1:title_tag.text.index("号")] )
  
    title = detail_content.find("div", {"class": "title"}).text.strip()
    title = title[title.index("号")+2:]
    case_info["Title"] = title
    case_info["Keywords"] = case.find("strong" , string= lambda text : "关键词" in text).parent.text.translate(translation_table).strip().removeprefix("关键词").strip()
    case_info["Url"] =  case_url
    case_info["Content"] = str(case)
    response.close()
    #except Exception as e:
        #print(case_url, ":", e)

    return  case_info


if __name__ == "__main__":

    test_url = "https://www.court.gov.cn/shenpan/xiangqing/382491.html"

    content = CaseParser(test_url)

    print(content)