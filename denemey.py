import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

from bs4 import BeautifulSoup as bs
from loggingmodule import LoggerObjects
from datetime import datetime
from lxml import html as _html
import numpy as np
import pandas as pd
from auxiliary.dataclass import BISTLiveData, BISTIndexData
from auxiliary.webelements import FTDivStandards, FTStockWebelements, FTIndexWebelements, FTDataTimeWebelements
from webautomation import SeleniumWebBrowser
from globals import Paths

from database.acquisition.historical_database import DSQuery
from acquisition.financialdata.current_data_acquisition import FTMainWindow, FTLogIn

class HTMLParser(BISTLiveData, FTDivStandards, FTStockWebelements, FTIndexWebelements, FTDataTimeWebelements, BISTIndexData):

    def __init__(self, html: str) -> None:
        self.logger = LoggerObjects.HTP_logger
        self.html = html
        self.soup : bs = None
        self.lxml = None
        self.data_datetime : np.datetime64 = None

    # HTML metnini elde eder.
    def __get_html(self) -> None:

        """
        HTML metnini elde eder.
        """

        self.soup = bs(self.html, 'lxml')
        self.lxml = _html.fromstring(self.html)
        return None
    
    # Zaman bilgisini elde eder.
    def __get_data_time(self) -> None:

        """
        Zaman bilgisini elde eder.
        """

        time_text = str(self.lxml.xpath(self.get_time_element(self.div1))[0])
        print("test2-timetext: ", time_text)
        if time_text is None:
            self.logger.warning("Zaman bilgisi elde edilemedi. Text değeri boş.")
            return None
        self.data_datetime = np.datetime64(datetime.combine(datetime.now().date(), datetime.strptime(time_text, '%H:%M:%S').time()), 's')
        print("test2-datetime: ", self.data_datetime)
        
        return None
    
    # Tarih verilerini elde eder.
    def __get_date_datas(self) -> None:
            
        """
        Deneme verilerini elde eder.
        """
        
        bugun_element : list = self.lxml.xpath("/html/body/div[4]/div/div/main/div/div/div[1]/div/div[1]")
        bugun_text : str = bugun_element[0].text
        if bugun_text is None:
            self.logger.warning("Bugün bilgisi elde edilemedi. Text değeri boş.")
            return None
        print("test3-bugun: ", bugun_text)
        
        gun_element : list = self.lxml.xpath("/html/body/div[4]/div/div/main/div/div/div[1]/div/div[2]")
        gun_text : str = gun_element[0].text
        if gun_text is None:
            self.logger.warning("Gün bilgisi elde edilemedi. Text değeri boş.")
            return None
        print("test3-gun: ", gun_text)
        
        return None
    
    # Endeks hacim verilerini elde eder.
    def __get_index_total_traded_value(self, stock_code: str, total_traded_volume: np.int64, total_traded_value: np.int64) -> None:
        
        """
        Endeks hacim verilerini elde eder.
        """
        
        i = 0                    
        # 1. kontrol noktası. Hisse istenen endekslere dahil değilse işlem yapmaz.
        if stock_code not in self.all_index_stocks:
            return None
        
        # 2. kontrol noktası. Hissenin hangi endekslerde yer aldığı belirlenir. 
        for _ in self.index_codes:
            
            if stock_code in self.index_sets[i]:
                self.add_index_total_traded_volume(i, total_traded_volume)
                self.add_index_total_traded_value(i, total_traded_value)
                
            i += 1
        
        return None
        
    # Sektör endeks verilerini elde eder.
    def __calculate_index_data(self, index_code: str) -> None:
        
        #########################################################################################################################################
        # !!!<GELİŞTİRİLECEK>!!!
        # Sektör endeks verileri ilgili endekse dahil hisse verileri ve önceden belirlenmiş endeks bölenleri/oranları kullanılarak elde edilecek.
        # !!!<GELİŞTİRİLECEK>!!!
        #########################################################################################################################################
        
        pass
    
    # Hisse verilerini elde eder.
    def __get_stock_data(self) -> None:
        
        """
        Hisse verilerini elde eder.
        """
        
        index = 1
        
        self.logger.debug("Hisse verileri elde ediliyor...")
                
        cards_count = 30 #len(self.all_index_stocks)
        
        while index <= cards_count:
            
            stock_code_text = np.str_(self.lxml.xpath(self.get_stock_code_webelement(self.div1, self.div2, index))[0])
            current_price_text = np.str_(self.lxml.xpath(self.get_current_price_webelement(self.div1, self.div2, index))[0])
            lowest_price_text = np.str_(self.lxml.xpath(self.get_lowest_price_webelement(self.div1, self.div2, index))[0])
            highest_price_text = np.str_(self.lxml.xpath(self.get_highest_price_webelement(self.div1, self.div2, index))[0])
            total_traded_volume_text = np.str_(self.lxml.xpath(self.get_total_traded_volume_webelement(self.div1, self.div2, index))[0])
            total_traded_value_text = np.str_(self.lxml.xpath(self.get_total_traded_value_webelement(self.div1, self.div2, index))[0])
            
            # Eğer herhangi bir veri eksikse döngüyü sonlandırır.
            if not all([stock_code_text, lowest_price_text, current_price_text, highest_price_text,total_traded_volume_text, total_traded_value_text]):
                print("test1-stockcount: ", index)
                break
            
            # Tip dönüşümleri yapılır.
            stock_code = np.str_(stock_code_text)
            lowest_price = np.float64(lowest_price_text.replace(",","."))
            current_price = np.float64(current_price_text.replace(",","."))
            highest_price = np.float64(highest_price_text.replace(",","."))
            total_traded_volume = np.int64(total_traded_volume_text.replace(".",""))
            total_traded_value = np.int64(total_traded_value_text.replace(".",""))
            
            # İstenen endekslere dahil olması halinde endeks hacim verileri elde edilir.
            #self.__get_index_total_traded_value(stock_code, total_traded_volume, total_traded_value)
            
            #  Veriler pandas.Series nesnesine dönüştürülür ve multiprocess Queue veri yapısına eklenir.
            stock_row = pd.Series([self.data_datetime, stock_code, lowest_price, current_price, highest_price, total_traded_volume, total_traded_value])
            self.stock_rows.put(stock_row)
            print("test1-stock: \n", stock_row, "\n")

            index += 1
        
        self.logger.debug("Hisse verileri elde edildi.")
        return None
    
    # Endeks verilerini elde eder.
    def __get_index_data(self) -> None:
        
        """
        Endeks verilerini elde eder.
        """
                
        self.logger.debug("Endeks değerleri elde ediliyor...")
        xu030_value_text = np.str_(self.lxml.xpath(self.get_xu030_value_webelement(self.div1, self.div2_index))[0])
        xu100_value_text = np.str_(self.lxml.xpath(self.get_xu100_value_webelement(self.div1, self.div2_index))[0])
                
        # Eğer herhangi bir veri eksikse işlemi sonlandırır.
        if not all([xu030_value_text, xu100_value_text]):
            return None
        
        # Tip dönüşümleri yapılır.
        xu030_value = np.float64(xu030_value_text.replace(",","."))
        xu100_value = np.float64(xu100_value_text.replace(",","."))
        
        # Dinamik olarak elde edilen endeks verilerini kuyruğa ekler.
        i = 0
        for index_code in ["XU030", "XU100"]: #self.index_codes:
            
            if index_code == self.xu030_code:
                xu030_index_row = pd.Series([self.data_datetime, self.xu030_code, xu030_value])#, self.index_total_traded_volumes[i], self.index_total_traded_values[i]])
                self.index_rows.put(xu030_index_row)
                print("test1-xu030: ", xu030_index_row)
                
            elif index_code == self.xu100_code:
                xu100_index_row = pd.Series([self.data_datetime, self.xu100_code, xu100_value])#, self.index_total_traded_volumes[i], self.index_total_traded_values[i]])
                self.index_rows.put(xu100_index_row)
                print("test1-xu100: ", xu100_index_row)
            
            else:
                index_row = pd.Series([self.data_datetime, index_code, self.index_values[i], self.index_total_traded_volumes[i], self.index_total_traded_values[i]])
                self.index_rows.put(index_row)
                print("test1-index: ", index_row)
                
            i += 1
                        
        self.logger.debug("Endeks değerleri elde edildi.")

        return None
    
    # HTML verilerini işleme metodu.
    def process_html(self) -> None:
        
        """
        HTML verilerini işleme metodu.
        """
        i = 1
        try:
            print("test1: ", i)
            self.__get_html()
            print("test2: ", i)
            self.__get_data_time()
            self.__get_date_datas()
            print("test3: ", i)
            self.__get_stock_data()
            print("test4: ", i)
            self.__get_index_data()
            print("test5: ", i)
            #self.__class__.raw_htmls.task_done()
            print("test6: ", i)
            
        except Exception as e:
            self.logger.warning("HTML verileri işlenemedi.")
            self.logger.debug(f"{e}")
            
        return None

if __name__ == "__main__":
    
    #browser = SeleniumWebBrowser(Paths.prefs_indirme).get_browser()
    DATETIME = "2024-06-24"
    data_query = DSQuery()
    data_query.get_all_stock_codes(index_codes= ["XU030"], start_date=DATETIME, end_date=DATETIME)
    data_query.get_index_stock_datas(index_codes= ["XU030"], date=DATETIME)
    
    print("test1: ", BISTIndexData.all_index_stocks)
    print("test2 :", data_query.all_index_stocks)
    
    """
    FTLogIn.perform_login(browser)
    FTMainWindow.perform_data_preparations(browser, data_query.all_index_stocks, "Küçük", "Özet")
    
    html_text_seleium = FTMainWindow(browser).get_page_source()
    
    with open(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\test.html", "w", encoding="utf-8") as file:
        file.write(html_text_seleium)

    if isinstance(html_text_seleium, str):
        pass
    
    else:
        print("HTML metni hatalı.")
        sys.exit()
        
    parser = HTMLParser(html_text_seleium)
    
    parser.process_html()
    
    print("Test başarıyla tamamlandı.")
    browser.quit()
    sys.exit()
    """
    