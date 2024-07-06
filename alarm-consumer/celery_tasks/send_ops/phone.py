from utils.logger import logger
def phone_send(alarm_list,post_data,userDict):
    try:
        for alarm_detail in alarm_list:
            send_to = alarm_detail.get('send_to',[])
            logger.info(f'phone_send>>>{send_to}')
            alarm_status = post_data.get('status','firing')
            phones = []
            for username in send_to:
                phones.append(userDict[username].get("phone",""))
            logger.debug(f'phones>>>{phones}')
    except Exception as e:
        logger.error(f'send phone err>>>{e}')