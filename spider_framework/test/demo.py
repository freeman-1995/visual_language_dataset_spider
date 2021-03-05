import requests
from lxml import  etree
url = "http://221.15.248.52:5100/item/?cid=98366995"
response = requests.get(url, headers={"user-agent": "chrom 80.0"},
                        )
print(response)
html=etree.HTML(response.text)
divs=html.xpath("//div")
item=dict()
for div in divs:
    spanList=div.xpath("./span/text()")
    key=spanList[0]
    key=key.replace(": ",'')
    if len(spanList)==1:
        value=""
    else:
        value=spanList[1]
    item[key]=value
print(item)