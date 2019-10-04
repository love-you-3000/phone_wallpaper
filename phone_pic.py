from pymongo import MongoClient,DESCENDING
import json
import re
import requests
import argparse


def get_answers_page(page_no):
    offset = page_no * 10
    url = 'https://www.zhihu.com/api/v4/questions/304706190/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset={}&platform=desktop&sort_by=default'.format(offset)
    headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
    r = requests.get(url,headers = headers)
    content = r.content.decode('utf-8')
    data = json.loads(content)
    is_end = data['paging']['is_end']
    items = data['data']
    client = MongoClient('mongodb://localhost:27017/')
    db = client['phonewallpaper']
    if len(items)>0:
        db.answer.insert_many(items)
    return is_end

def get_answers():
    page_no = 0
    client = MongoClient('mongodb://localhost:27017/')
    while True:
        print(page_no)
        is_end = get_answers_page(page_no)
        page_no +=1
        if is_end:
            break

def query():
    img_urls = []
    client = MongoClient('mongodb://localhost:27017/')
    db = client['phonewallpaper']
    items = db.answer.find({"voteup_count":{"$gte":100}}).sort([("voteup_count",DESCENDING)])
    count = 0
    f = open('result_text.txt','w+')
    for item in items:
        content = item["content"]
        vote_num = item["voteup_count"]
        author = item['author']['name']
        matched = re.findall(r'data-original="(.*?)"',content)
        f.write(">来自:{}\n".format(item['url']))
        f.write(">作者:{}\n".format(author))
        f.write(">赞数:{}\n".format(vote_num))
        for img_url in matched:
            if img_url not in img_urls:
                img_urls.append(img_url)
        count += len(img_urls)
        f.write("\n\n")
    return img_urls

def download():
    img_urls = query()
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
    i = 1
    for url in img_urls:
        print(url)
        filepic = open(r'phone_pic/%s.jpg'%i,'wb')
        filepic.write(requests.get(url,headers=headers).content)
        filepic.close()
        i += 1
    print('共%d张壁纸'%i)
    print('下载完成！')
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save",help="save data",action="store_true",dest="save")
    parser.add_argument("--query",help="query data",action="store_true",dest="query")
    parser.add_argument("--download", help="download data", action="store_true", dest="download")
    args = parser.parse_args()

    if args.save:
        get_answers()
    elif args.query:
        query()
    elif args.download:
        download()




