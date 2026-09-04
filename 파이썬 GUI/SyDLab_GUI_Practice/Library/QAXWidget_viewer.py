import time
import requests
import lxml
from bs4 import BeautifulSoup
from PyQt5.QtCore import *

class BitCoin_thread(QThread):
    data_sending = pyqtSignal(list)

    def __init__(self, parent = None):
        super(BitCoin_thread,self).__init__(parent)


    def run(self):
        while True:
            headers = {
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
            }

            html = requests.get('https://finance.yahoo.com/quote/BTC-USD', headers=headers).text

            soup = BeautifulSoup(html, 'lxml')

            Bitcoin = soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
            Bitcoin_percent = soup.select('span[class*="Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px)"]')[0].get_text()

            self.data_sending.emit([Bitcoin, Bitcoin_percent])
            time.sleep(2)