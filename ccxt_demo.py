# -*-coding:utf-8-*-
'''
@File    :   build_demo.py
@Contact :   Tao1148852798@Gmail.com
@License :   (C)Copyright 2020

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021-11-15 上午8:57   TaoXianLong   3.7        None
'''
import requests
from lxml import etree
import pandas as pd
import ccxt


def build_ip_pool():
    url = 'https://ip.ihuan.me/address/576O5Zu9.html?page='
    page = ['b97827cc', '4ce63706', '5crfe930', 'f3k1d581', 'ce1d45977']
    ip = '//a[@target="_blank"]/text()'
    port = '//tbody/tr/td[2]/text()'
    httpsif = '//tbody/tr/td[5]/text()'
    paths = []
    for i in page:
        paths.append(url + i)
    ips, ports, httpsifs = [], [], []
    for path in paths:
        response = requests.get(path)
        e = etree.HTML(response.text)
        info1 = e.xpath(ip)
        for i in info1:
            ips.append(i)
        info2 = e.xpath(port)
        for i in info2:
            ports.append(i)
        info3 = e.xpath(httpsif)
        for i in info3:
            httpsifs.append(i)
    while '89代理ip' or '申请友链' in ips:
        try:
            ips.remove('89代理ip')
        except BaseException:
            break
        try:
            ips.remove('申请友链')
        except BaseException:
            break
    ips = pd.DataFrame(ips)
    ports = pd.DataFrame(ports)
    httpsifs = pd.DataFrame(httpsifs)
    pool = pd.concat([ips, ports, httpsifs], axis=1)
    pool.columns = ['ip', 'port', 'httpsif']
    pool = pool[pool['httpsif'] == '支持']
    pool['input'] = pool['ip'] + ':' + pool['port']
    return pool.reset_index(drop=True)


def binance(ip, symbol: []):
    binance_exchange = ccxt.binance({
        'apiKey': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'timeout': 15000,
        'enableRateLimit': True,
        'proxies': {'https': "{}".format(ip.strip())}
    })
    FundingRate = binance_exchange.fapiPublic_get_premiumindex()

    def getdata(symbol: [], FundingRate):
        FundingRate_pd = pd.DataFrame(FundingRate)
        res = []
        for key in symbol:
            rate = FundingRate_pd[FundingRate_pd['symbol'] == '{}'.format(key)]['lastFundingRate']
            rate_percent = (str(float(rate) * 100))[:7] + '%'
            res.append(rate_percent)
        return res

    return getdata(symbol, FundingRate)


def send_gamil(body):
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    gmail_user = 'xxxxxxxxxx.com'
    gmail_password = 'xxxxxxxx'

    sent_from = gmail_user
    to = ['xxxxxxxx@qq.com']
    import time
    localtime = time.asctime(time.localtime(time.time()))

    message = MIMEText(body, 'plain', 'utf-8')
    subject = '今日{}币安资金费率情况 Binance FundingRate Info'.format(localtime)
    message['Subject'] = Header(subject, 'utf-8')

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, message.as_string())
    server.close()


if __name__ == '__main__':
    proxy, error = pd.DataFrame(), ''
    while proxy.empty:
        try:
            proxy = build_ip_pool()
        except Exception as e:
            error = e
    ips = list(proxy['input'])
    no = 0
    symbol, info, flag = ['ETHUSDT', 'KLAYUSDT'], '', 'F'
    while flag == 'F':
        try:
            if no < len(ips):
                info = binance(ips[no], symbol)
            else:
                break
        except Exception as e:
            print('E', e)
            no += 1
        else:
            flag = 'T'

    d = str(dict(zip(symbol, info)))
    send_gamil(d)

