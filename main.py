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
import os
import signal
import logging
import random
import subprocess
import ast
import itertools
import win32com.client
import pythoncom
import wmi

class maxProfit:
    coin            = 0
    coinAcron       = 1
    coinInfos       = 2
    profitability24 = 3
    profitability   = 4
    poolServer      = 5
    poolPort        = 6

class processIdx:
    processMonitor      = 0
    processLuncher      = 1
    processLuncherLast  = 2

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

global maxProfitInfo;
maxProfitInfo = ["no_coin", "", "", 0, 0, {}, {}];
global lastMaxProfitInfo;
lastMaxProfitInfo = ["no_coin", "", "", 0, 0, {}, {}];
#luncherMiners = dict([ ("Ethereum", "C:\Claymore\EthDcrMiner64.exe \-epool %s \-ewal 0xe8a6ce621385b940eb0a73b18c78a3c5773bf4a2 \-epsw x \-wd 0")])
luncherMiners = dict([ ("Ethereum", ".\Claymore\EthDcrMiner64.exe -wd 1 -r 1 -epool stratum+tcp://%s -ewal 0xe8a6ce621385b940eb0a73b18c78a3c5773bf4a2 -esm 0 -epsw x -allpools 1 -mport -%s -asm 1"),
                       ("Zencash",  ".\ZecMiner\miner.exe --server %s --user znS42ysFP43wBW8yKbf2xVyRuHbQevzguKC --pass x --port %s --cuda_devices 0 1 2 3")])
#global luncher;
__luncher= "";

#logging.basicConfig(level=logging.DEBUG,
#                    format='(%(threadName)-10s) ',
#                    )
global processHldr;
processHldr = [0, 0, 0]

def worker(__workerName__):
    """thread worker function"""
    print "Worker: ", __workerName__;
    return

def killWin32Process():
    pythoncom.CoInitialize ()
    WMI = win32com.client.GetObject('winmgmts:')
    processes = WMI.InstancesOf('Win32_Process')
    for process in processes:
        pid = process.Properties_('ProcessID').Value
        parent = process.Properties_('ParentProcessId').Value
        #print pid, parent
        try :
            if (processHldr[processIdx.processMonitor].pid == parent):
                print( "process to kill ", pid, "parent = ", parent);
                subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=pid))
        except ValueError:
            print("error in PID ")

    pythoncom.CoUninitialize ()

def determinateBestProfitable( __lastMaxProfitInfo__, __maxProfitInfo__):
    print "BROWSER check"
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request('http://whattomine.com/coins.json', None, headers)
    url = urllib2.urlopen(req).read()
    urllib2.urlopen(req).close()

    __object__ = json.loads(url.decode())
    #pprint ( __object__)
    lastCoin = __lastMaxProfitInfo__[maxProfit.coin]
    for coinType in coinsDictionnary:
        if(__lastMaxProfitInfo__[maxProfit.coin] ==  coinType):
            #print ("update the new info related to the last coin", __maxProfitInfo__[maxProfit.coin])
            __lastMaxProfitInfo__[maxProfit.profitability]      = __object__['coins'][coinType]['profitability'];
            __lastMaxProfitInfo__[maxProfit.profitability24]    = __object__['coins'][coinType]['profitability24'];
            __lastMaxProfitInfo__[maxProfit.coinAcron]          = __object__['coins'][coinType]['tag'].lower();
            __lastMaxProfitInfo__[maxProfit.coin]               = __maxProfitInfo__[maxProfit.coin];

    __maxProfitInfo__[maxProfit.profitability24] = 0;
    __maxProfitInfo__[maxProfit.profitability] = 0;
    __maxProfitInfo__[maxProfit.coin] = "";
    __maxProfitInfo__[maxProfit.coinAcron] = 0;

    for coinType in coinsDictionnary:
        if(__object__['coins'][coinType]['profitability24'] > __maxProfitInfo__[maxProfit.profitability24]):
            __maxProfitInfo__[maxProfit.profitability24] = __object__['coins'][coinType]['profitability24'];
            __maxProfitInfo__[maxProfit.coin] = coinType;
            __maxProfitInfo__[maxProfit.coinAcron] = __object__['coins'][coinType]['tag'].lower();

        if(__object__['coins'][coinType]['profitability'] > __maxProfitInfo__[maxProfit.profitability]):
            __maxProfitInfo__[maxProfit.profitability] = __object__['coins'][coinType]['profitability'];

    print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability24]);
    print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability]);
    if (__maxProfitInfo__[maxProfit.coin] != __lastMaxProfitInfo__[maxProfit.coin] and __lastMaxProfitInfo__[maxProfit.coin] != "no_coin"):
            if (processHldr[processIdx.processLuncher] != ""):
                print ("Process will be killed ")
                pool.makeActive("workerMonitorMinerCmd")
                killWin32Process()

    __lastMaxProfitInfo__[maxProfit.coin] = __maxProfitInfo__[maxProfit.coin]

    print ("coin =", __lastMaxProfitInfo__[maxProfit.coin])

def bestPoolSeeker(__url__, __cryptoCoin__, __maxProfitInfo__, __lastMaxProfitInfo__):
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
    __lastMaxProfitInfo__ = __maxProfitInfo__[:]
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
            determinateBestProfitable(lastMaxProfitInfo, maxProfitInfo);
            print("lastMaxProfitInfo ::: ")
            url = "https://investoon.com/mining_pools/";
            bestPoolSeeker(url, maxProfitInfo[maxProfit.coinAcron], maxProfitInfo, lastMaxProfitInfo);
            time.sleep(10)

            port =  str(maxProfitInfo[maxProfit.poolPort]).split(',',1)
            server =  str(maxProfitInfo[maxProfit.poolServer]).split(',',1)
            print " lunchminer ", luncherMiners[maxProfitInfo[maxProfit.coin]]
            if (maxProfitInfo[maxProfit.coin] == "Ethereum"):
                processHldr[processIdx.processLuncher] = luncherMiners[maxProfitInfo[maxProfit.coin]] %(str(server[0]) + ":" + str(port[0]), str(port[0]))
            if (maxProfitInfo[maxProfit.coin] == "Zencash"):
                processHldr[processIdx.processLuncher] = luncherMiners[maxProfitInfo[maxProfit.coin]] %(str(server[0]), str(port[0]))
            print " luncher ", processHldr[processIdx.processLuncher]
            #print("Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort])
            pprint(maxProfitInfo)

def workerMonitorMinerCmd(s, pool):
    print('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        while True:
            pool.makeActive(name)
            print('Starting : cmdLuncher ', processHldr[processIdx.processLuncher]);
            if (processHldr[processIdx.processLuncherLast] != processHldr[processIdx.processLuncher]):
                if (0 != processHldr[processIdx.processMonitor]):
                    print "kill process :: ", processHldr[processIdx.processLuncher]
                run_win_cmd(processHldr[processIdx.processLuncher]);
                processHldr[processIdx.processLuncherLast] = processHldr[processIdx.processLuncher];

            print("process PID =", processHldr[processIdx.processLuncher]);
            time.sleep(10)
            pool.makeInactive(name)

def monitoringData():
    while True:
        logging.debug('Starting : monitoring data for max profit coin and pool');
        determinateBestProfitable(data, lastMaxProfitInfo, maxProfitInfo);
        url = "https://investoon.com/mining_pools/";
        bestPoolSeeker(url, maxProfitInfo[maxProfit.coinAcron], maxProfitInfo);
        print "Servers :  ", maxProfitInfo[maxProfit.poolServer], " | ", maxProfitInfo[maxProfit.poolPort]
        print "infos server and max profit "
        pprint(maxProfitInfo)
        logging.debug('Exiting')

def run_win_cmd(cmd):
    result = []
    DETACHED_PROCESS = 0x00000008

    print "function run_win_cmd", cmd
    processHldr[processIdx.processMonitor] = subprocess.Popen(cmd,
                                                                shell=True,
                                                                stdout=subprocess.PIPE,
                                                                stderr=subprocess.PIPE,
#                                                                preexec_fn=os.setsid,
                                                                creationflags=DETACHED_PROCESS)
    #process.communicate();
    #processHldr[processIdx.processMonitor].terminate()
    for line in processHldr[processIdx.processMonitor].stdout:
        result.append(line)
        errcode = processHldr[processIdx.processMonitor].returncode
        for line in result:
            print(line)
#    if errcode is not None:
#        raise Exception('cmd %s failed, see above for details', cmd)

print ("################################")
print ("######     RigManager     ######")
print ("################################")

pool = ActivePool()
s = threading.Semaphore(2)
tH1 = threading.Thread(target=workerMonitorData, name="workerMonitorData", args=(s, pool))
tH1.start()
time.sleep(30)
tH2 = threading.Thread(target=workerMonitorMinerCmd, name="workerMonitorMinerCmd", args=(s, pool))
tH2.start()
