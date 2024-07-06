import requests
import json
import datetime
import traceback
def send_wechat(wx_users, wx_title, wx_content):
    send_result = True
    try:
        corpid = 'ww20e43468f6a541f4'
        corpsecret = 'iHOzaEBiQNhnafBs75HCBDpzBNmtPZ9AplrJ02QhSR8'
        token_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format(corpid, corpsecret)
        token_resp = requests.get(token_url, timeout=3)
        print(token_resp.json())
        if token_resp.status_code == 200:
            ac_token = token_resp.json().get('access_token')
            touser = "|".join(wx_users)
            request_body = {
                "touser": touser,
                "msgtype": "textcard",
                "agentid": 1000003,
                "textcard":
                    {
                        "title":
                            wx_title,
                        "description":
                            "<div class=\"gray\">{0}</div><div class=\"normal\">{1}</div>".format(
                                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), wx_content
                            ),
                        "url":"http://baidu.com",
                    },

                "enable_id_trans": 0,
                "enable_duplicate_check": 0
            }
            resp = requests.post(
                url='https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}'.format(ac_token),
                json=request_body,
                timeout=3
            )
            print('send_wechat_msg: {0} {1}'.format(touser, resp.json()))
    except Exception:
        send_result = False
        print(traceback.format_exc())
    return send_result

# 企业微信相关信息
corpid = "1"
corpsecret = "WyklWDadcpreZC5rJBUTXYpwSUsdTBp4BrNP3t775bU"
agentid = "1000003"
touser = ""  # @all表示向所有用户发送告警，可以替换为特定的用户ID
message = "测试微信告警发送！"

# 发送告警
send_wechat(['zxli22'], '测试微信告警发送', '托管测试')