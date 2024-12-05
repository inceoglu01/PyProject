import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

import time
from datetime import datetime, time as _time, date as _date
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
import lxml
from lxml import etree as _html

from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from typing import override

from dataclass import StockExchangeTime, BISTLiveData
from webautomation import SeleniumWebElementAttributes as SWA
from webelements import FTLogInWebelements, FTMainWindowWebelements, FTDataTimeWebelements, FTWebElementStandards, FTDivStandards, FTStockWebelements, FTIndexWebelements
from webelements import FTCardTabs as CardTabs

import selenium.webdriver as _webdriver
from selenium.webdriver.common.keys import Keys

from webautomation import SeleniumWebBrowser
from loggingmodule import LoggerObjects
from errorhandling import ErrorHandling
from globals import LoginInfo, Paths, WebSites
from controlsystems import time_interval, SubjectBase, ObserverBase

from database.acquisition.historical_database import DSQuery, BISTIndexData

from acquisition.acquisition import LogInBase, MainWindowBase, AcquisitionBase

# FinTables sitesine giriş yapma işlemleri.
class FTLogIn(LogInBase, FTDivStandards, FTLogInWebelements):

    """
    FTLogIn sınıfı, FinTables sitesine giriş yapma işlemlerini gerçekleştirebilmek için gerekli değişken
    ve metodları içerir.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FTLogIn, cls).__new__(cls)
        return cls._instance
        
    # Tanımlamalar
    def __init__(self, browser: _webdriver.Chrome):
        if not hasattr(self, '_initialized'):
            super().__init__(browser, LoggerObjects.FLI_logger)
            self.username = LoginInfo.email
            self.password = LoginInfo.ft_password
            self._initialized = True
            
    # FinTables sitesine giriş için gerekli web elementleri elde eder.
    def __get_login_webelements(self) -> None:

        """
        Fintables sitesine giriş için gerekli web elementlerini elde eder.
        """

        self.logger.debug("Giriş için gerekli web elementleri elde ediliyor...")

        self.__class__.email_input = self.wait_for_element(*self.login_email_tuple, 6)
        self.logger.debug("Email alanı elde edildi.")

        self.__class__.password_input = self.wait_for_element(*self.login_password_tuple, 6)
        self.logger.debug("Şifre alanı elde edildi.")

        self.__class__.login_button = self.wait_for_element(*self.login_button_tuple, 6)
        self.logger.debug("Giriş yap butonu elde edildi.")
        
        self.logger.debug("Giriş için gerekli web elementleri elde edildi.")
        return None
            
    # FinTables sitesine giriş yapar.
    def __login(self) -> None:

        """
        Fintables sitesine giriş yapar.
        """

        self.logger.info("Email ve şifre alanlarına bilgiler giriliyor.")
        self.send_keys(self.email_input, self.username)
        self.logger.info("Email alanına bilgiler girildi.")
        time.sleep(1)
        self.send_keys(self.password_input, self.password)
        self.logger.info("Şifre alanına bilgiler girildi.")
        time.sleep(1)
        self.click(self.login_button)
        self.logger.info("Giriş yap butonuna tıklandı.")
        time.sleep(3)
        self.logger.info("Siteye giriş yapıldı.")
        return None

    # FinTables sitesine giriş yapar.
    @staticmethod
    def perform_login(browser: _webdriver.Chrome) -> None:

        """
        FinTables sitesine giriş yapar.
        """

        G_logger = LoggerObjects.FLI_logger

        G_logger.debug("FinTables sitesine giriş yapılıyor...")

        login = FTLogIn(browser)

        login.open_website(WebSites.fintables)

        login.__get_login_webelements()

        login.__login()

        G_logger.debug("FinTables sitesine giriş yapıldı.")
        return None

# FinTables sitesindeki ana pencere işlemleri.
class FTMainWindow(MainWindowBase, FTDivStandards, FTMainWindowWebelements):

    """
    FTMainWindow sınıfı, FinTables sitesinden anlık veri elde etme işlemlerini gerçekleştirebilmek için gerekli değişken
    ve metodları içerir.
    """
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FTMainWindow, cls).__new__(cls)
        return cls._instance

    # Tanımlamalar
    def __init__(self, browser: _webdriver.Chrome):
        if not hasattr(self, '_initialized'):
            super().__init__(browser, LoggerObjects.FMW_logger)
            self.add_cards_error = False
            self._initialized = True
            
    # Kart görünüm seçme butonu.
    def __set_layout(self, layout_type: str = FTMainWindowWebelements.layout_small) -> None:

        """
        Kart görünüm seçme butonuna tıklar.
        """

        def click_layout_menu_button() -> None:

            self.__class__.layout_menu_button = self.wait_for_element(*self.get_layout_menu_button(self.div1, self.div2), 6)
            self.click(self.layout_menu_button)
            self.logger.debug("Görünüm menüsü butonuna tıklandı.")
            time.sleep(1)
            return None
        
        def select_layout_type(layout_type: str = self.layout_small) -> None:

            click_layout_menu_button()
            self.__class__.layout_small_button = self.wait_for_element(*self.get_layout_button(self.layout_small), 6)
            self.__class__.layout_big_button = self.wait_for_element(*self.get_layout_button(self.layout_big), 6)
            self.logger.debug("Kart görünümü butonları elde edildi.")

            if layout_type == self.layout_small:
                self.click(self.layout_small_button)
                self.logger.debug("Küçük kart görünümü seçildi.")
                time.sleep(1)
            elif layout_type == self.layout_big:
                self.click(self.layout_big_button)
                self.logger.debug("Büyük kart görünümü seçildi.")
                time.sleep(1)
            else:
                self.logger.critical("Geçersiz kart görünümü seçimi yapıldı. Tekrar deneyin.")
                
            return None
        
        return select_layout_type(layout_type)

    # Hisse kartı ekleme butonu.
    def __get_add_cards_webelements(self) -> None:

        """
        Hisse kartı ekleme ile ilgili webelementleri elde eder.
        """

        self.__class__.add_button = self.wait_for_element(*self.get_add_button(self.div1, self.div2), 6)
        self.click(self.add_button)
        self.__class__.stock_input = self.wait_for_element(*self.get_stock_input(self.div3), 6)
        self.click(self.add_button)
        self.logger.debug("Hisse kartı ekleme webelementleri elde edildi.")

        return None

    # Hisse kartlarını siteye ekler.
    def add_cards(self, stock_codes: list[str] | set[str], layout_type: str = FTMainWindowWebelements.layout_small) -> None:

        """
        Hisse kartlarını siteye ekler.
        """
        
        if not (isinstance(stock_codes, list) or isinstance(stock_codes, set)):
            raise ValueError("Hisse kodları uygun formatta değil. Hisse kodlarını kontrol edin.")
        
        if isinstance(stock_codes, set):
            stock_codes = sorted(stock_codes)
        
        def add_cards_core(stock_code: str) -> bool:
            
            try:
                self.click(self.add_button)
                self.send_keys(self.stock_input, stock_code)
                self.send_keys(self.stock_input, Keys.ENTER)
                self.logger.debug(stock_code + " hisse kartı eklendi.")
                self.add_cards_error = True
                
            except:
                self.logger.error(stock_code + " hisse kartı eklenemedi.")
                self.add_cards_error = False

            return None

        self.logger.debug("Hisse kartları ekleme işlemi başlatıldı")

        self.__set_layout(layout_type)
        self.logger.debug("Hisse kartları görünümü ayarlandı.")
        self.__get_add_cards_webelements()
        
        if stock_codes == None:
            self.logger.critical("Hisse kartları ekleme işlemi için hisse kodları bulunamadı.")
            self.logger.critical("Çıkış yapılıyor.")
            sys.exit()

        for stock_code in stock_codes:

            self.add_cards_error = False
            while not self.add_cards_error:

                add_cards_core(stock_code)
                if not self.add_cards_error:
                    self.__get_add_cards_webelements()
                    
        self.logger.debug("Hisse kartları ekleme işlemi tamamlandı.")

        return None

    # Kart sekmelerine tıklama metodu.
    def click_card_tabs(self, tab_name: str) -> None:
        
        """
        Kart sekmelerine tıklama metodu.
        """
        
        def get_card_webelements(tab_name: str) -> None:
            i = 0

            while True:
                
                self.__class__.all_card_tabs = self.wait_for_elements(*self.get_tab_button(tab_name), 6)
                
                if self.__class__.all_card_tabs != None:
                    self.logger.debug("Kart sekmesi webelementleri elde edildi.")
                    break
                
                if i == 3:
                    self.logger.critical("Kart sekmeleri birden fazla kez elde edilemedi.")
                    self.logger.debug(f"Eklenemeyen kart sekmesinin ismi/stringi: {tab_name}")
                    self.logger.critical("Çıkış yapılıyor.")
                    sys.exit()
                    
                i += 1
                
        def get_unopened_card_tabs() -> None:
            
            self.__class__.unopened_card_tabs = [x for x in self.all_card_tabs if self.get_attribute(x, "aria-selected") == "false"]
        
        def click_card_tabs() -> None:
                        
            for card_tab in self.unopened_card_tabs or []:
                self.click(card_tab)
                
            time.sleep(1)
            self.logger.debug("Kart sekmelerine tıklandı.")
            return None
        
        while True:
            
            get_card_webelements(tab_name)
            get_unopened_card_tabs()
            click_card_tabs()
            
            if len(self.unopened_card_tabs) == 0:
                break

        return None

    # Ana pencere işlemleri.
    @staticmethod
    def perform_data_preparations(browser: _webdriver.Chrome, stock_codes: list[str] | set[str], layout_type: str, data_tab: str) -> None:
            
        """
        Ana pencere işlemleri.
        """

        if data_tab not in [value for key, value in CardTabs.__dict__.items() if not key.startswith('__')]:
            raise ValueError("Geçersiz kart sekmesi ismi. Sekme ismini kontrol edin.")

        F_logger = LoggerObjects.FMW_logger # FT-FTM: FinTables - Ana Pencere

        F_logger.debug("FinTables sitesindeki ana pencere işlemleri başlatılıyor...")

        mainwindow = FTMainWindow(browser) # Ana pencere sınıfından bir nesne oluşturur.

        mainwindow.add_cards(stock_codes, layout_type)

        mainwindow.click_card_tabs(data_tab)

        F_logger.debug("FinTables sitesindeki ana pencere işlemleri tamamlandı.")

        return None
    
# Yayın zamanı ve saatini elde etme işlemleri.
class FTDataTimeACQ(AcquisitionBase, FTDataTimeWebelements, SubjectBase, FTDivStandards):

    """
    FTDataTimeACQ sınıfı, FinTables sitesindeki veri yayın zamanını elde etme ve güncelleme işlemlerini gerçekleştirebilmek için gerekli değişken
    ve metodları içerir.
    """
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FTDataTimeACQ, cls).__new__(cls)
        return cls._instance
        
    def __init__(self, browser: _webdriver.Chrome) -> None:
        if not hasattr(self, '_initialized'):
            AcquisitionBase.__init__(self, browser, LoggerObjects.FTD_logger)
            FTDataTimeWebelements.__init__(self)
            SubjectBase.__init__(self)
            self.data_date : _date = None
            self.data_time : _time = None
            self.data_datetime : datetime = None
            self._initialized = True
    
    # Zaman web elementini elde eder.
    def __get_time_webelement(self) -> None:

        """
        Fintables sitesindeki zaman web elementini elde eder.
        """

        self.__class__.time_webelement = self.wait_for_element(*self.get_time_webelement(self.div1), 6)
        self.logger.debug("Zaman web elementi elde edildi.")
        return None

    # Veri yayın zamanını elde eder fakat güncelleme yapmaz. Kontrol amaçlı kullanılır.
    def __control_data_time(self) -> datetime | None:

        """
        Anlık veri yayın zamanını elde eder fakat herhangi bir güncelleme yapmaz. Kontrol amaçlı kullanılır.
        """
        
        time_text = self.get_attribute(self.time_webelement, SWA.text)
        if time_text is None:
            return None
        data_time = datetime.combine(self.data_date, datetime.strptime(time_text, '%H:%M:%S').time())
        
        return data_time

    # Veri yayın zamanını günceller.
    def __get_data_time(self) -> None:
        
        """
        Veri yayın zamanını (data_datetime) günceller.
        """
        
        data_time_str = self.get_attribute(self.time_webelement, SWA.text)
        # Eğer veri yayın zamanı stringi elde edilemezse işlem yapmaz.
        if data_time_str is None:
            pass
        self.data_datetime = datetime.combine(self.data_date, datetime.strptime(data_time_str, '%H:%M:%S').time())

        return None

    # Veri yayın zamanı kontrol metodu.
    def __control_time(self) -> None:

        """
        Anlık veri yayın saatine göre kontrol yapar. Her saniyede bir veri yayın zamanını ve veri saatini (data_clock) günceller.
        """
        
        if self.data_datetime == self.__control_data_time():
            pass

        else:
            self.__get_data_time()
            self.notify()

        return None
    
    # Veri zamanı güncelleme metodu.
    @time_interval(LoggerObjects.FTD_logger, StockExchangeTime.bist_exchange_opening_time, StockExchangeTime.bist_exchange_closing_time)
    def update_data_time(self) -> None:
        
        """
        Fintables sitesinde bulunan veri yayın zamanına göre veri zamanını günceller.
        """

        ##############################################################################################################
        # ThreadErrorHandling sınıfı decoratorleri ile birlikte kullanılmalıdır.
        ##############################################################################################################
        
        self.__get_time_webelement()
        self.data_date = datetime.now().date()

        while datetime.now().time() < StockExchangeTime.bist_exchange_closing_time:
            
            self.__control_time()

        return None

class FTLiveDataACQ(AcquisitionBase, ObserverBase, BISTLiveData):

    """
    FTLiveData sınıfı Fintables sitesinin kaynağını HTML metin biçimde elde eder.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls._instance = super(FTLiveDataACQ, cls).__new__(cls)
        return cls._instance

    def __init__(self, browser: _webdriver.Chrome) -> None:
        if not hasattr(self, '_initialized'):
            AcquisitionBase.__init__(self, browser, LoggerObjects.FLD_logger)
            ObserverBase.__init__(self)
            BISTLiveData.__init__(self)
            self._initialized = True
        
    @override
    def update(self) -> None:
        
        self.__class__.raw_htmls.put(self.get_page_source())
        
        return None

# !!!ÇALIŞMIYOR, ÇALIŞILAN KÜTÜPHANE DEĞİŞTİRİLEBİLİR!!!
class HTMLParser(BISTLiveData, FTDivStandards, FTStockWebelements, FTIndexWebelements, FTDataTimeWebelements, BISTIndexData):

    def __init__(self) -> None:
        self.logger = LoggerObjects.HTP_logger
        self.soup : bs = None
        self.lxml = None
        self.data_datetime : np.datetime64 = None

    # HTML metnini elde eder.
    def __get_html(self) -> None:

        """
        HTML metnini elde eder.
        """

        raw_html = self.__class__.raw_htmls.get()
        self.soup = bs(raw_html, 'lxml')
        self.lxml = _html.HTML(raw_html)
        return None
    
    # Zaman bilgisini elde eder.
    def __get_data_time(self) -> None:

        """
        Zaman bilgisini elde eder.
        """

        time_element : list = self.lxml.xpath(self.get_time_element(self.div1))
        time_text : str = time_element[0].text
        if time_text is None:
            self.logger.warning("Zaman bilgisi elde edilemedi. Text değeri boş.")
            return None
        self.data_datetime = np.datetime64(datetime.combine((datetime.now().date(), 'D'), datetime.strptime(time_text, '%H:%M:%S').time()), 's')
        
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
                
        cards_count = len(self.all_index_stocks)
        
        while index <= cards_count:
            
            stock_code_text : str = self.lxml.xpath(self.get_stock_code_webelement(self.div1, self.div2, index))
            current_price_text : str = self.lxml.xpath(self.get_current_price_webelement(self.div1, self.div2, index))
            lowest_price_text : str = self.lxml.xpath(self.get_lowest_price_webelement(self.div1, self.div2, index))
            highest_price_text : str = self.lxml.xpath(self.get_highest_price_webelement(self.div1, self.div2, index))
            total_traded_volume_text : str = self.lxml.xpath(self.get_total_traded_volume_webelement(self.div1, self.div2, index))
            total_traded_value_text : str = self.lxml.xpath(self.get_total_traded_value_webelement(self.div1, self.div2, index))

            # Eğer herhangi bir veri eksikse döngüyü sonlandırır.
            if not all([stock_code_text, lowest_price_text, current_price_text, highest_price_text,total_traded_volume_text, total_traded_value_text]):
                break
            
            # Tip dönüşümleri yapılır.
            stock_code = np.str_(stock_code_text)
            lowest_price = np.float64(lowest_price_text.replace(",","."))
            current_price = np.float64(current_price_text.replace(",","."))
            highest_price = np.float64(highest_price_text.replace(",","."))
            total_traded_volume = np.int64(total_traded_volume_text.replace(".",""))
            total_traded_value = np.int64(total_traded_value_text.replace(".",""))
            
            # İstenen endekslere dahil olması halinde endeks hacim verileri elde edilir.
            self.__get_index_total_traded_value(stock_code, total_traded_volume, total_traded_value)
            
            #  Veriler pandas.Series nesnesine dönüştürülür ve multiprocess Queue veri yapısına eklenir.
            stock_row = pd.Series([self.data_datetime, stock_code, lowest_price, current_price, highest_price, total_traded_volume, total_traded_value])
            self.stock_rows.put(stock_row)
            print("test1-stock: ", stock_row)

            index += 1
        
        self.logger.debug("Hisse verileri elde edildi.")
        return None
    
    # Endeks verilerini elde eder.
    def __get_index_data(self) -> None:
        
        """
        Endeks verilerini elde eder.
        """
                
        self.logger.debug("Endeks değerleri elde ediliyor...")
        xu030_value_text : str = self.lxml.xpath(self.get_xu030_value_webelement(self.div1, self.div2_index))
        xu100_value_text : str = self.lxml.xpath(self.get_xu100_value_webelement(self.div1, self.div2_index))
        
        # Eğer herhangi bir veri eksikse işlemi sonlandırır.
        if not all([xu030_value_text, xu100_value_text]):
            return None
        
        # Tip dönüşümleri yapılır.
        xu030_value = np.float64(xu030_value_text.replace(",","."))
        xu100_value = np.float64(xu100_value_text.replace(",","."))
        
        # Dinamik olarak elde edilen endeks verilerini kuyruğa ekler.
        i = 0
        for index_code in self.index_codes:
            
            if index_code == self.xu030_code:
                xu030_index_row = pd.Series([self.data_datetime, self.xu030_code, xu030_value, self.index_total_traded_volumes[i], self.index_total_traded_values[i]])
                self.index_rows.put(xu030_index_row)
                print("test1-xu030: ", xu030_index_row)
                
            elif index_code == self.xu100_code:
                xu100_index_row = pd.Series([self.data_datetime, self.xu100_code, xu100_value, self.index_total_traded_volumes[i], self.index_total_traded_values[i]])
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
    @time_interval(LoggerObjects.HTP_logger, StockExchangeTime.bist_exchange_opening_time, StockExchangeTime.bist_exchange_closing_time)
    def process_html(self) -> None:
        
        """
        HTML verilerini işleme metodu.
        """
        i = 1
        while datetime.now().time() < StockExchangeTime.bist_exchange_closing_time:
            try:
                print("test1: ", i)
                self.__get_html()
                print("test2: ", i)
                self.__get_data_time()
                print("test3: ", i)
                self.__get_stock_data()
                print("test4: ", i)
                self.__get_index_data()
                print("test5: ", i)
                self.__class__.raw_htmls.task_done()
                print("test6: ", i)
                
            except Exception as e:
                self.logger.warning("HTML verileri işlenemedi.")
                self.logger.debug({e})
                
            i += 1
            
        return None
    
# Fintables sitesinden canlı veri elde etme fonksiyonu.
@ErrorHandling.unexpected_error(logger=LoggerObjects.CDA_logger, gmessage= "Hisse verileri elde etme modülü tamamlanamadı.", exit= True)
def ft_live_data() -> None:

    """
    Bu fonksiyon, FinTables sitesine giriş yapar, FinTables sitesinden webscrapping yöntemi ile borsa verilerini elde eder.
    
    Gösterge endekslerinin ve BIST-030 endeksine dahil olan hisselerin anlık verilerini multithreading yöntemi ile elde eder.
    """
    DATETIME = "2024-06-24"
    cda_logger = LoggerObjects.CDA_logger
    
    cda_logger.info("Hisse verileri modülü başlatıldı.")
    
    # Veritabanı işlemleri
    data_query = DSQuery()
    data_query.get_all_stock_codes(index_codes= ["XU030"], start_date=DATETIME, end_date=DATETIME)
    data_query.get_index_stock_datas(index_codes= ["XU030"], date=DATETIME)

    # Ana program işlemleri hazırlığı.
    cda_logger.info("Tarayıcı başlatılıyor.")
    browser = SeleniumWebBrowser(Paths.prefs_indirme).get_browser()
    
    ftwebelementstandards = FTWebElementStandards() # Bağlam problemleri
    datatime_acq = FTDataTimeACQ(browser)
    live_data_acq = FTLiveDataACQ(browser)
    html_parser = HTMLParser()
    
    datatime_acq.attach(live_data_acq)
    ftwebelementstandards.set_standard_value(False)
    ftwebelementstandards.set_webelement_standard()
    
    # Ana program işlemleri.
    FTLogIn.perform_login(browser)

    FTMainWindow.perform_data_preparations(browser, data_query.all_index_stocks, FTMainWindowWebelements.layout_small, CardTabs.tab_ozet)
    
    with ThreadPoolExecutor() as executor:

        # Veri yayın zamanı güncelleme işlemleri. Webscrapping.
        executor.submit(datatime_acq.update_data_time)
        
        # Canlı veri elde etme işlemleri. Webscrapping.
        for _ in range(2):
            executor.submit(html_parser.process_html)

    cda_logger.info("Tarayıcı kapatılıyor.")
    browser.quit()
    cda_logger.info("Tarayıcı kapatıldı.")

    cda_logger.info("Hisse verileri elde etme modülü başarıyla tamamlandı.")
    return None

def test_process_html() -> None:
    
    while True:
        
        row_series = BISTLiveData.stock_rows.get()
        print("test1: \n", row_series)
        print(type(row_series))
        BISTLiveData.stock_rows.task_done()
        
    return None

if __name__ == "__main__":
    
    html_str = open(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\output.txt", "r", encoding="utf-8").read() 
    lxml_html = _html.HTML(html_str)
    time_element : list = lxml_html.xpath(FTDataTimeWebelements.get_time_element(FTDivStandards.div1))
    print(time_element)
    time_text : str = time_element[0].text
    print(time_text)
    