import requests
import json
import urllib3
import itertools

urllib3.disable_warnings()

BASE_URL = "https://dekt.hfut.edu.cn/scReports/api/wx/netlearning"
KEY_SESSION = ''  # 学号

HEADERS = {
    'Host': 'dekt.hfut.edu.cn',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
    'content-type': 'application/json',
    'Referer':
    'https://servicewechat.com/wx1e3feaf804330562/67/page-frame.html'
}


def get_articles():
    articles = []
    # 只获取每列的100项
    url = BASE_URL + "/page/1/100"
    for i in range(3):
        payload = json.dumps({"category": "", "columnType": str(i)})
        headers = {'key_session': KEY_SESSION, **HEADERS}
        response = requests.request("POST",
                                    url,
                                    headers=headers,
                                    data=payload,
                                    verify=False)
        articles.extend(json.loads(response.text)['data']['list'])
    return articles


def get_question(id: str):
    url = f"{BASE_URL}/questions/{id}"
    payload = {}
    secret = '66a6d6358388f52cb3a41c67efa9f7e2'
    headers = {'key_session': KEY_SESSION, 'secret': secret, **HEADERS}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)['data']['questions'][0]
    que_id = response['id']
    optionList = [i['id'] for i in response['optionList']]
    return que_id, optionList


def submit_answer(que_id, option_list):
    url = f"{BASE_URL}/answer/{que_id}"
    payload = json.dumps(option_list)
    headers = {'key_session': KEY_SESSION, **HEADERS}
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)


def get_answer(option_list: list):
    res = []
    for i in range(1, len(option_list) + 1):
        for j in itertools.combinations(option_list, i):
            res.append(list(j))
    return res


if __name__ == '__main__':
    articles = get_articles()
    finish = False
    for article in articles:
        if finish:
            break
        if article['correct'] == '已完成':
            continue
        print(article['title'], ":")
        que_id, option_list = get_question(article['id'])
        answers = get_answer(option_list)
        for answer in answers:
            res = submit_answer(que_id, answer)
            if res['code'] == '200':
                if res['data']['code'] == '1014':
                    print("\t回答错误")
                    continue
                else:
                    print('\t', res['data']['desc'])
                    break
            else:
                print("\t" + res['errMsg'])
                finish = True
                break
