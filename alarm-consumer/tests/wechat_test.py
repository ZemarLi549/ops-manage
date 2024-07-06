import requests
import json
def send_wechat(webhook_url,content):
    resp = requests.post(webhook_url,data=json.dumps(content))
    print(resp.text)

LEVEL_PIC = {
    'disaster':'https://pic.imgdb.cn/item/65570357c458853aef6eff10.jpg',
    'normal':'https://pic.imgdb.cn/item/65570357c458853aef6eff2c.jpg',
    'recovery':'https://pic.imgdb.cn/item/65570357c458853aef6eff42.jpg',
    'serious':'https://pic.imgdb.cn/item/65570357c458853aef6eff6b.jpg',
    'urgent':'https://pic.imgdb.cn/item/65570357c458853aef6eff84.jpg',
}
if __name__ == '__main__':
    alarm_id='33021'
    alarm_title='测试告警001'
    webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0f81ba52-6f44-46cf-b181-b7346e4a3496'
    # content_msg = {
    # "msgtype": "markdown",
    #     "markdown": {
    #         "content": f'''应用托管告警\n
    #         >告警ID：<font color=\"comment\">{alarm_id}</font>
    #         >告警标题：<font color=\"comment\">{alarm_title}</font> \n <@李增鑫>''',
    #     }
    # }
    content_msg ={
    "msgtype":"template_card",
    "template_card":{
        "card_type":"news_notice",
        "source":{
            "icon_url":"https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
            "desc":"企业微信",
            "desc_color":0
        },
        "card_image":{
            "url":"https://pic.imgdb.cn/item/65570357c458853aef6eff2c.jpg",
            "aspect_ratio":2.25
        },
        "main_title":{
            "title":"欢迎使用企业微信",
            "desc":"您的好友正在邀请您加入企业微信"
        },

        "quote_area":{
            "type":1,
            "url":"https://work.weixin.qq.com/?from=openApi",
            "appid":"APPID",
            "pagepath":"PAGEPATH",
            "title":"引用文本标题",
            "quote_text":"Jack：企业微信真的很好用~\nBalian：超级好的一款软件！"
        },
        "vertical_content_list":[
            {
                "title":"惊喜红包等你来拿",
                "desc":"下载企业微信还能抢红包！"
            }
        ],
        "horizontal_content_list":[
            {
                "keyname":"邀请人",
                "value":"张三"
            },
            {
                "keyname":"企微官网",
                "value":"点击访问",
                "type":1,
                "url":"https://work.weixin.qq.com/?from=openApi"
            },
            {
                "keyname":"企微下载",
                "value":"企业微信.apk",
                "type":2,
                "media_id":"MEDIAID"
            }
        ],
        "jump_list":[
            {
                "type":1,
                "url":"https://work.weixin.qq.com/?from=openApi",
                "title":"企业微信官网"
            },
            {
                "type":2,
                "appid":"APPID",
                "pagepath":"PAGEPATH",
                "title":"跳转小程序"
            }
        ],
        "card_action":{
            "type":1,
            "url":"https://work.weixin.qq.com/?from=openApi",
            "appid":"APPID",
            "pagepath":"PAGEPATH"
        }
    }
}

    send_wechat(webhook_url,content_msg)