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

class maxProfit:
    coin            = 0
    coin2           = 1
    profitability24 = 2
    profitability   = 3

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
                    ,"PascalLite"
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

maxProfitInfo = ["", "", 0, 0];


headers = { 'User-Agent' : 'Mozilla/5.0' }
req = urllib2.Request('https://whattomine.com/coins.json', None, headers)
url = urllib2.urlopen(req).read()
data = json.loads(url.decode())
#pprint(json.dumps(data, sort_keys=False))
#pprint(data)
#print(data['coins']['Ethereum'])

#def loadProfitabilityJsonInfo(__object__, __url__):
#    req = urllib2.Request(__url__, None, headers);
#    urlPage = urllib2.urlopen(req).read()
#    __object__ = json.loads(urlPage.decode());


def determinateBestProfitable(__object__, __maxProfitInfo__):
#    __maxProfitInfo__[maxProfit.coin] = __object__['coins'][0];
#    __maxProfitInfo__[maxProfit.profitability24] = __object__['coins'][0]['profitability24'];

    for coinType in coinsDictionnary:
 #       print "profitability24 : ", __maxProfitInfo__[maxProfit.profitability24]
 #       print "web profitability24 : ", __object__['coins'][coinType]['profitability24']
        if(__object__['coins'][coinType]['profitability24'] > __maxProfitInfo__[maxProfit.profitability24]):
            __maxProfitInfo__[maxProfit.profitability24] = __object__['coins'][coinType]['profitability24'];
            __maxProfitInfo__[maxProfit.coin] = coinType;

        if(__object__['coins'][coinType]['profitability'] > __maxProfitInfo__[maxProfit.profitability]):
            __maxProfitInfo__[maxProfit.profitability] = __object__['coins'][coinType]['profitability'];
            __maxProfitInfo__[maxProfit.coin2] = coinType;


    print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability24]);
    print ("The max profitable cryptocurrency = ", __maxProfitInfo__[maxProfit.coin], " with profitability within : ", __maxProfitInfo__[maxProfit.profitability]);


def bestPoolSeeker(__url__, __cryptoCoin__):
    display = Display(visible=0, size=(800, 600))
    display.start()
    browser = webdriver.Firefox()
    fullUrl = __url__+__cryptoCoin__;
    browser.get(fullUrl);
    print browser.title
    table = browser.find_element_by_tag_name("tbody");
    all_rows = table.find_elements_by_tag_name("tr")
    print "rows One", all_rows[1].text
    cells = all_rows[1].find_elements_by_tag_name("td")
    print ("Coins = ", cells[0].text)
    browser.quit()
    display.stop()

print ("################################")
print ("######     RigManager     ######")
print ("################################")


#loadProfitabilityJsonInfo(data, "https://whattomine.com/coins.json");
#pprint(data);
determinateBestProfitable(data, maxProfitInfo);
url = "https://investoon.com/mining_pools/";
bestPoolSeeker(url, "eth");
#print len(data['coins'])
