import requests
from urllib.parse import quote,unquote
def sendsms(phones, content):
    sms_send_url = 'http://dcsms.com/api/ten/tencentcloud/tencloudsms.action'
    paltform_pass = '24a62954-4670-9721-d0ae0214296d'
    msg = unquote(content)
    payload = {'uuid': paltform_pass,
               'params': str([msg]),
               'type_num': '2',
               'iphone': str(phones)}
    headers = {}
    files = []
    r = requests.request(
        "POST", sms_send_url, headers=headers, data=payload, files=files)
    print(f'sendmss resp:{r.text}')
    return r.json()['code']

phones = ['13524622011']
result = '[告警触发]|告警名称:cpu使用率过高|级别:一般|项目组件:aops-tengine|主题:测试告警001|实例:10.110.1.29|告警ID:3303|详情:(http://127.0.0.1:8098/#/alarmdetail?alarmid=18)|处理:(http://127.0.0.1:8098/#/alarmedit?alarmid=18)'
sendsms(phones, quote(result,safe='', encoding="utf-8"))