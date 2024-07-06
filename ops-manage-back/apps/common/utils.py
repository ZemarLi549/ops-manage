# -*- coding: utf-8 -*-
import datetime
import time
import pandas as pd
def get_datetime_now():
    return datetime.datetime.now()

def strtime2int(time_str, format='%Y-%m-%dT%H:%M:%S'):
    time_int = int(time.mktime(time.strptime(time_str.split('.')[0], format)) * 1000)
    return time_int
def count_kuadu(fromTime,toTime):
    fromTime = strtime2int(fromTime.replace(' ', 'T'))
    toTime = strtime2int(toTime.replace(' ', 'T'))
    kuadu = int((toTime - fromTime) / 1000)
    if kuadu > 60 and kuadu <= 60 * 20:
        step = '1m'
    elif kuadu > 60 * 20 and kuadu <= 60 * 60*1:
        step = '5m'
    elif kuadu > 60 * 60 * 1 and kuadu <= 60 * 60 * 2:
        step = '10m'
    elif kuadu > 60 * 60*2 and kuadu <= 60 * 60*24:
        step = '1h'
    elif kuadu > 60 * 60 * 24 and kuadu <= 60 * 60 * 24 * 3:
        step = '4h'
    elif kuadu > 60 * 60 * 24 * 3 and kuadu <= 60 * 60 * 24 * 5:
        step = '12h'
    elif kuadu > 60 * 60 * 24 * 5:
        step = '1d'
    else:
        step = '5s'

    if 's' in step:
        formatstr = "%y/%m/%d-%H:%M:%S"
    elif 'm' in step:
        formatstr = "%y/%m/%d-%H:%M"
    elif 'd' in step:
        formatstr = "%y/%m/%d"
    else:
        formatstr = "%y/%m/%d-%H"
    return step,formatstr

def format_time(india_time_str, local_format,india_format='%Y-%m-%dT%H:%M:%S.%fZ',add_time=True):
    # int格式说明加工了

    if isinstance(india_time_str, int) or india_time_str.isdigit():
        if len(str(india_time_str)) > 10:
            timeid = int(str(india_time_str)[:10])
            time_str = time.strftime(local_format, time.localtime(timeid))
        else:
            time_str = time.strftime(local_format, time.localtime(india_time_str))
        return time_str

    india_dt = datetime.datetime.strptime(india_time_str, india_format)
    if add_time:
        india_dt+=datetime.timedelta(hours=8)
    time_str = india_dt.strftime(local_format)
    return time_str

def alarm_format_time(india_time_str, local_format,india_format='%Y-%m-%dT%H:%M:%S.%fZ',add_time=True):
    # int格式说明加工了

    if isinstance(india_time_str, int) or india_time_str.isdigit():
        if len(str(india_time_str)) > 10:
            timeid = int(str(india_time_str)[:10])
            timeid-= 28800
            time_str = time.strftime(local_format, time.localtime(timeid))
        else:
            india_time_str = int(str(india_time_str))-28800
            time_str = time.strftime(local_format, time.localtime(india_time_str))

        return time_str

    india_dt = datetime.datetime.strptime(india_time_str, india_format)
    if add_time:
        india_dt+=datetime.timedelta(hours=8)
    time_str = india_dt.strftime(local_format)
    return time_str

def ms_format_time(india_time_str, local_format='%Y-%m-%d %H:%M:%S',india_format='%Y-%m-%dT%H:%M:%S.%fZ',add_time=True):
    #int格式说明加工了
    try:
        india_time_str = int(india_time_str)
    except:pass
    if isinstance(india_time_str,int) or india_time_str.isdigit():
        if len(str(india_time_str)) > 10:
            timeid = int(str(india_time_str)[:10])
            time_str = time.strftime(local_format, time.localtime(timeid)) + '.' + str(india_time_str)[-3:]
        else:
            time_str = time.strftime(local_format, time.localtime(india_time_str))
        return time_str
    ms_str = india_time_str.split('.')[-1]
    india_dt = datetime.datetime.strptime(india_time_str, india_format)
    if add_time:
        india_dt+=datetime.timedelta(hours=8)
    time_str = india_dt.strftime(local_format)
    return time_str+f'.{ms_str.replace("Z","")}'


def pd_return(resp_,x_str,y_str,val_str):
    messages = []
    xList = []
    if resp_:
        df = pd.DataFrame(list(resp_))
        gp = df.groupby([x_str, y_str]).agg({val_str: sum})
        newdf = gp.unstack().fillna(0)
        com_ls = zip(*list(newdf.columns))
        col_list = list(list(com_ls)[1]) if list(newdf.columns) else []
        newdf.columns = col_list
        xList = list(newdf.index)
        for col_str in col_list:
            dict_ = {y_str: col_str, 'yList': list(newdf.loc[:, col_str])}
            messages.append(dict_)
    return xList, messages