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
import subprocess
import ast

class maxProfit:
    coin            = 0
    coinAcron       = 1
    coinInfos       = 2
    profitability24 = 3
    profitability   = 4
    poolServer      = 5
    poolPort        = 6

class processIdx:
    processMonitor  = 0
    processLuncher  = 1

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
luncherMiners = dict([ ("Ethereum", ".\Claymore\EthDcrMiner64.exe -wd 1 -r 1 -epool stratum+tcp://%s -ewal $WALLET -esm 0 -epsw x -allpools 1 -mport -%s -asm 1")])
#logging.basicConfig(level=logging.DEBUG,
#                    format='(%(threadName)-10s) ',
#                    )

processHldr = [0, 0]
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

    print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability24]);
    print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability]);

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
    __maxProfitInfo__[maxProfit.poolServer] = ast.literal_eval(json.dumps(server))
    __maxProfitInfo__[maxProfit.poolPort]   = ast.literal_eval(json.dumps(port))
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
            port =  str(maxProfitInfo[maxProfit.poolPort]).split(',',1)
            server =  str(maxProfitInfo[maxProfit.poolServer]).split(',',1)
            processHldr[processIdx.processLuncher] = luncherMiners[maxProfitInfo[maxProfit.coin]] %(str(server[0]) + ":" + str(port[0]), str(port[0]))
            #print("Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort])
            pprint(maxProfitInfo)

def workerMonitorMinerCmd(s, pool):
    print('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        while True:
            pool.makeActive(name)
            print('Starting : cmdLuncher ');
            run_win_cmd(processHldr[processIdx.processLuncher]);
            time.sleep(10000)
            pool.makeInactive(name)

def monitoringData():
    while True:
        logging.debug('Starting : monitoring data for max profit coin and pool');
        determinateBestProfitable(data, maxProfitInfo);
        url = "https://investoon.com/mining_pools/";
        bestPoolSeeker(url, maxProfitInfo[maxProfit.coinAcron], maxProfitInfo);
        print "Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort]
        print "infos server and max profit "
        pprint(maxProfitInfo)
        time.sleep(20)
        logging.debug('Exiting')

def run_win_cmd(cmd):
    result = []
    DETACHED_PROCESS = 0x00000008

    print "function run_win_cmd"
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               creationflags=DETACHED_PROCESS)
    print "output : ", process
    processHldr[processIdx.processMonitor] = process.pid
    #process.communicate();
    print "process : ", process
    print "process output", process.stdout
    process.poll()
    print "process : ", process
    for line in process.stdout:
        result.append(line)
        errcode = process.returncode
        for line in result:
            print(line)
    if errcode is not None:
        raise Exception('cmd %s failed, see above for details', cmd)
print ("################################")
print ("######     RigManager     ######")
print ("################################")

pool = ActivePool()
s = threading.Semaphore(2)
tH1 = threading.Thread(target=workerMonitorData, name="workerMonitorData", args=(s, pool))
tH1.start()
tH2 = threading.Thread(target=workerMonitorMinerCmd, name="workerMonitorMinerCmd", args=(s, pool))
tH2.start()
