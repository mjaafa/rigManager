# /usr/bin/env python
import urllib2, json
from pprint import pprint
import enum
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import threading
import time
import logging
import sys
import multiprocessing
import logging
import random

class maxProfit:
    coin            = 0
    coinAcron       = 1
    coinInfos       = 2
    profitability24 = 3
    profitability   = 4
    poolServer      = 5
    poolPort        = 6

coinsDictionnary = [ "BitcoinGold"
                    ,"Bytecoin"
                    ,"DGB-Groestl"
                    ,"Decred"
                    ,"DigitalNote"
                    ,"Electroneum"
                    ,"Ellaism"
                    ,"Ethereum"
                    ,"EthereumClassic"
                    ,"Expanse"
                    ,"Feathercoin"
                    ,"GoByte"
                    ,"GroestlCoin"
                    ,"Halcyon"
                    ,"Hush"
                    ,"Karbo"
                    ,"Komodo"
                    ,"LBRY"
                    ,"Metaverse"
                    ,"Monacoin"
                    ,"Monero"
                    ,"Musicoin"
                    ,"Myriad-Groestl"
                    ,"Orbitcoin"
                    ,"Pascalcoin"
                    ,"Pirl"
                    ,"Sia"
                    ,"Sibcoin"
                    ,"Sumokoin"
                    ,"Trezarcoin"
                    ,"Ubiq"
                    ,"Verge-Groestl"
                    ,"Verge-Lyra2REv2"
                    ,"Vertcoin"
                    ,"Vivo"
                    ,"Zcash"
                    ,"Zclassic"
                    ,"Zencash"];

maxProfitInfo = ["", "", "", 0, 0, {}, {}];
#logging.basicConfig(level=logging.DEBUG,
#                    format='(%(threadName)-10s) ',
#                    )

headers = { 'User-Agent' : 'Mozilla/5.0' }
req = urllib2.Request('https://whattomine.com/coins.json', None, headers)
url = urllib2.urlopen(req).read()
data = json.loads(url.decode())
coins = data['coins'];
#pprint (data['coins']['Ethereum']['tag'].lower())

def worker(__workerName__):
    """thread worker function"""
    print "Worker: ", __workerName__;
    return

def determinateBestProfitable(__object__, __maxProfitInfo__):

    for coinType in coinsDictionnary:
        if(__object__['coins'][coinType]['profitability24'] > __maxProfitInfo__[maxProfit.profitability24]):
            __maxProfitInfo__[maxProfit.profitability24] = __object__['coins'][coinType]['profitability24'];
            __maxProfitInfo__[maxProfit.coin] = coinType;
            __maxProfitInfo__[maxProfit.coinAcron] = __object__['coins'][coinType]['tag'].lower();

        if(__object__['coins'][coinType]['profitability'] > __maxProfitInfo__[maxProfit.profitability]):
            __maxProfitInfo__[maxProfit.profitability] = __object__['coins'][coinType]['profitability'];

    #print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability24]);
    #print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability]);


def bestPoolSeeker(__url__, __cryptoCoin__, __maxProfitInfo__):
    browser = webdriver.PhantomJS()
    fullUrl = __url__+__cryptoCoin__;
    browser.get(fullUrl);
    print browser.title
    table = browser.find_element_by_tag_name("tbody");
    #print "table : ", table.text
    all_rows = table.find_elements_by_tag_name("tr")
    __maxProfitInfo__[maxProfit.coinInfos] = all_rows[1].text
    cells = all_rows[2].find_elements_by_tag_name("td")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    _table_ = soup.find('tr', attrs={"class": u"table-pool"})
    rowz = _table_.findAll("td");
    server  = _table_['data-child-server']
    port    = _table_['data-child-port']
    __maxProfitInfo__[maxProfit.poolServer] = server.split();
    __maxProfitInfo__[maxProfit.poolPort]   = port.split();
    browser.quit()

class ActivePool(object):
    def __init__(self):
        super(ActivePool, self).__init__()
        self.active = []
        self.lock = threading.Lock()
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            #logging.debug('Running: %s', self.active)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            #logging.debug('Running: %s', self.active)

def workerMonitorData(s, pool):
    print('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        while True:
            pool.makeActive(name)
            print('Starting : monitoring data for max profit coin and pool');
            determinateBestProfitable(data, maxProfitInfo);
            url = "https://investoon.com/mining_pools/";
            bestPoolSeeker(url, maxProfitInfo[maxProfit.coinAcron], maxProfitInfo);
            time.sleep(10)
            pool.makeInactive(name)
            #print("Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort])
            pprint(maxProfitInfo)

def monitoringData():
    while True:
        logging.debug('Starting : monitoring data for max profit coin and pool');
        determinateBestProfitable(data, maxProfitInfo);
        url = "https://investoon.com/mining_pools/";
        bestPoolSeeker(url, maxProfitInfo[maxProfit.coinAcron], maxProfitInfo);
#        maxProfitInfo[maxProfit.poolServer]  = ['eu1.ethermine.org,eu2.ethermine.org,asia1.ethermine.org,us1.ethermine.org,us2.ethermine.org']
#        maxProfitInfo[maxProfit.poolPort] = ['4444,4444,4444,4444,4444']
#        maxProfitInfo[maxProfit.coin] = 'Ethereum';
#        maxProfitInfo[maxProfit.coinAcron] = 'eth';
#        maxProfitInfo[maxProfit.coinInfos] = 'F2pool\nMin Payout: 0.1 ETH\nHashRate: 20.5 TH/s\nDifficulty: 4 Billion\nETH PPS cn 3.0 %';
#        maxProfitInfo[maxProfit.profitability] = 100;
#        maxProfitInfo[maxProfit.profitability24] = 100;

        print "Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort]
        print "infos server and max profit "
        pprint(maxProfitInfo)
        time.sleep(20)
        logging.debug('Exiting')

def monitoringDataPrc():
    proc_ = multiprocessing.current_process()

    print "Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort], proc_.name, proc_.pid
    while True:
        sys.stdout.flush();
        logging.debug('Starting : monitoring data for max profit coin and pool');
        determinateBestProfitable(data, maxProfitInfo);
        url = "https://investoon.com/mining_pools/";
        bestPoolSeeker(url, maxProfitInfo[maxProfit.coinAcron], maxProfitInfo);
#        maxProfitInfo[maxProfit.poolServer]  = ['eu1.ethermine.org,eu2.ethermine.org,asia1.ethermine.org,us1.ethermine.org,us2.ethermine.org']
#        maxProfitInfo[maxProfit.poolPort] = ['4444,4444,4444,4444,4444']
#        maxProfitInfo[maxProfit.coin] = 'Ethereum';
#        maxProfitInfo[maxProfit.coinAcron] = 'eth';
#        maxProfitInfo[maxProfit.coinInfos] = 'F2pool\nMin Payout: 0.1 ETH\nHashRate: 20.5 TH/s\nDifficulty: 4 Billion\nETH PPS cn 3.0 %';
#        maxProfitInfo[maxProfit.profitability] = 100;
#        maxProfitInfo[maxProfit.profitability24] = 100;

        print "Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort]
        print "infos server and max profit "
        pprint(maxProfitInfo)
        time.sleep(20)
        logging.debug('Exiting')
        sys.stdout.flush();

print ("################################")
print ("######     RigManager     ######")
print ("################################")

pool = ActivePool()
s = threading.Semaphore(2)
for i in range(1):
    t = threading.Thread(target=workerMonitorData, name="workerMonitorData", args=(s, pool))
    t.start()
#monitoringDataTask = threading.Thread(name='monitoringData', target=monitoringData)
#monitoringDataTask.setDaemon(True);
#monitoringDataTask = multiprocessing.Process(name='daemon', target=monitoringDataPrc)
#monitoringDataTask.daemon = True;
#monitoringDataTask.start();
#monitoringDataTask.join();

