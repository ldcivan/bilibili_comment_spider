import requests
import time
import json
import csv


page = 1  # 起始页面
bvid = 'BV1Xq4y177qq'  # BV号
cookie = {'SESSDATA': ''}  # cookie，一般不需要，死活爬不出来再加


# 读取已写入的评论，并防止重复写入
existing_comments = set()
with open('data.csv', 'a', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            for row in reader:
                existing_comments.add(row[1])  # 注意，若改变了csv_data的顺序，这里也要跟着改
        except:
            pass


def add(data):  # 添加评论与点赞数
    # 打开CSV文件，如果文件不存在则创建一个新的，注意这个写入会在原文件上直接加而不会覆盖
    with open('data.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        comment = data[0]
        if comment not in existing_comments:  # 排除重复用，实际上会误伤很多内容
        # if True:
            writer.writerow(data)
            existing_comments.add(comment)
        else:
            print('pass')


def get_one_reply(rpid, rp_page):  # 楼中楼爬取
    re_url = f'https://api.bilibili.com/x/v2/reply/reply?oid={bvid}&pn={rp_page}&root={rpid}&type=1'
    response = requests.get(re_url, cookies=cookie)
    data = json.loads(response.text)
    code = data['code']  # 判断获取的页面是否正常
    if code != 0 or len(data['data']['replies']) == 0:
        print("reply：返回了code：", code, "，replies列表长度：", len(data['data']['replies']), "可能是到达页尾或被bilibili风控")
        raise Exception('已到达页尾')
    for j in range(len(data['data']['replies'])):  # 遍历所有评论的数据块
        mid = data['data']['replies'][j]['member']['mid']
        comment = data['data']['replies'][j]['content']['message']  # 摘取评论与点赞数
        like = data['data']['replies'][j]['like']
        create_time = data['data']['replies'][j]['ctime']
        print(mid, comment, like, create_time)
        csv_data = [mid, comment, like, create_time]
        add(csv_data)
    print(f'评论下回复{rp_page}页爬取完成')
    time.sleep(1.2)  # 调整爬取间隔，建议大于1200毫秒


def get_one_page(page):  # 获取主评论，并获取楼中楼root_id
    url = f'https://api.bilibili.com/x/v2/reply/main?next={page}&type=1&oid={bvid}&mode=3'
    response = requests.get(url, cookies=cookie)
    data = json.loads(response.text)
    code = data['code']  # 判断获取的页面是否正常
    if code != 0 or len(data['data']['replies']) == 0:
        print("main：返回了code：", code, "，replies列表长度：", len(data['data']['replies']), "可能是到达页尾或被bilibili风控")
        raise Exception('已到达页尾')
    for j in range(len(data['data']['replies'])):  # 遍历所有评论的数据块
        mid = data['data']['replies'][j]['member']['mid']
        comment = data['data']['replies'][j]['content']['message']  # 摘取评论与点赞数
        like = data['data']['replies'][j]['like']
        create_time = data['data']['replies'][j]['ctime']
        rpid = data['data']['replies'][j]['rpid']
        print(mid, comment, like, create_time)
        csv_data = [mid, comment, like, create_time]
        add(csv_data)
        rp_page = 1
        while True:
            try:
                get_one_reply(rpid, rp_page)
                rp_page = rp_page + 1
            except:
                print('评论下回复爬取完成')
                break
    print(page, '页结束')
    time.sleep(1.2)  # 调整爬取间隔，建议大于1200毫秒



while True:
    try:
        get_one_page(page)
        page = page + 1
    except:
        print('完毕')
        break
