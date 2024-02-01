from pymongo import MongoClient

import caseparser

connection_string = "mongodb://localhost:27017"

client = MongoClient(connection_string)

db = client["scfroot"]
collection = db["cases.directive"]
#先删除集合内的数据
collection.drop()
  
case_url_list, case_url_bad_list = caseparser.CaseListFetch(1)

for case_url in case_url_list:
    case_content = caseparser.CaseParser(case_url)
    # 写入集合
    collection.insert_one(case_content)
client.close()

print("bad url:", case_url_bad_list)



