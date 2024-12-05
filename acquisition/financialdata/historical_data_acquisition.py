import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

import time
from datetime import datetime, time as dt_time

import os

from webautomation import DSLogInWebelements, DSFilterWebelements, DSProductFilterStrings, DSDownloadWebelements

from concurrent.futures import ThreadPoolExecutor, wait

import selenium.webdriver as webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.select import Select

from loggingmodule import LoggerObjects
from errorhandling import ErrorHandling
from globals import LoginInfo, Paths, WebSites
from sqlalchemy import create_engine, MetaData

from database.database import HistoricalDataModul, conn_string, DatabaseNames, DatabaseTables
from acquisition.acquisition import LogInBase, SeleniumBase

class DSLogIn(LogInBase, DSLogInWebelements):

    """
    DSLogIn sınıfı, BIST DataStore sitesine giriş yapma işlemlerini gerçekleştirebilmek için gerekli değişken
    ve metodları içerir.
    """

    def __init__(self, browser: webdriver.Chrome) -> None:
        super().__init__(browser)

    # Giriş bilgilerini girer.
    def enter_login_info(self) -> None:

        """
        BIST DataStore sitesine giriş yapma işlemi için gerekli olan e-posta ve şifre bilgilerini girer.
        """

        def login_core() -> None:

            try:
                self.logger.debug("E-posta ve şifre giriş alanlarına veri giriliyor...")
                self.email_input.send_keys(LoginInfo.email)
                self.logger.debug("E-posta giriş alanına veri girildi.")
                self.password_input.send_keys(LoginInfo.ds_password)
                self.logger.debug("Şifre giriş alanına veri girildi.")
                self.__class__.login_error_value = False
                self.logger.debug("E-posta ve şifre giriş alanlarına veri girildi.")
                return None
            
            except:
                self.logger.debug("E-posta veya şifre giriş alanlarına veri girilirken bir hata oluştu.")
                self.__class__.login_error_value = True
                return None
        
        def enter_login_info() -> None:

            z = 0

            while self.login_error_value:

                login_core()
                z += 1

                if z == 3:
                    self.logger.critical("E-posta veya şifre giriş alanlarına birden fazla kez veri girilemedi.")
                    self.logger.debug(f"E-posta veya şifre giriş alanlarına veri girilme deneme sayısı: {z}")
                    self.logger.critical("Çıkış yapılıyor.")
                    sys.exit()

            self.logger.debug(f"E-posta veya şifre giriş alanlarına veri girilme deneme sayısı: {z}")
            return None

        return enter_login_info()

    # Giriş yapma işlemi için gerekli web elementlerini elde eder.
    def get_webelements(self) -> None:

        """
        Giriş yapma işlemi için gerekli web elementlerini elde eder.
        """

        @ErrorHandling.timeout_error(logger = self.logger, emessage= "E-posta giriş alanı bulunamadı.", gmessage = "E-posta giriş alanı bulunamadı.",  exit = True)
        def get_email_input() -> None:

            self.__class__.email_input = WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.login_email_input_tuple))
            self.logger.debug(f"E-posta giriş alanı webelementi elde edildi.")
            return None

        @ErrorHandling.timeout_error(logger = self.logger, emessage= "Şifre giriş alanı bulunamadı.", gmessage = "Şifre giriş alanı bulunamadı.", exit = True)
        def get_password_input() -> None:
                
            self.__class__.password_input = WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.login_password_input_tuple))
            self.logger.debug(f"Şifre giriş alanı webelementi elde edildi.")
            return None
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage= "Doğrulama kodu giriş alanı bulunamadı.", gmessage = "Doğrulama kodu giriş alanı bulunamadı.", exit = True)
        def get_verification_code_input() -> None:
                    
            self.__class__.verification_code_input = WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.login_verification_code_input_tuple))
            self.logger.debug(f"Doğrulama kodu giriş alanı webelementi elde edildi.")
            return None
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage= "Giriş yap butonu bulunamadı.", gmessage = "Giriş yap butonu bulunamadı.", exit = True)
        def get_login_button() -> None:
                            
            self.__class__.login_button = WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.login_button_tuple))
            self.logger.debug(f"Giriş yap butonu webelementi elde edildi.")
            return None

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Giriş yapma işlemi için gerekli web elementleri alınamadı.", exit = True)
        def get_webelements() -> None:
            
            self.logger.debug("Giriş yapma işlemi için gerekli web elementleri alınıyor.")
            get_email_input()
            get_password_input()
            get_verification_code_input()
            get_login_button()
            self.logger.debug("Giriş yapma işlemi için gerekli web elementleri alındı.")

            return None
        
        return get_webelements()

    # Doğrulama kodu giriş işlemi sırasında alınan hataları kontrol eder.
    def __get_verification_error_code(self) -> None:

        """
        Doğrulama kodu giriş işlemi sırasında alınan hataları kontrol eder ve hata varsa True, yoksa False döndürür.
        """
        
        # Hatalı doğrulama kodu uyarısı alındıysa True, alınmadıysa False döndürür.
        self.logger.debug("Hatalı doğrulama kodu uyarısı kontrol ediliyor.")
        try:
            self.__class__.wrong_code_webelement = WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(self.login_wrong_verification_code_tuple)) # Yanlış doğrulama kodu uyarısı
            self.__class__.wrong_verification_code = self.wrong_code_webelement.is_displayed()
        
        except:
            self.__class__.wrong_verification_code = False
        self.logger.debug("Hatalı doğrulama kodu uyarısı kontrol edildi.")
        
        # Boş doğrulama kodu uyarısı alındıysa True, alınmadıysa False döndürür.    
        self.logger.debug("'Boş doğrulama kodu' uyarısı kontrol ediliyor.")
        try:
            self.__class__.empty_code_webelement = WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(self.login_empty_verification_code_tuple)) # 'Boş doğrulama kodu' uyarısı
            self.__class__.empty_verification_code = self.empty_code_webelement.is_displayed()
        
        except:
            self.__class__.empty_verification_code = False
        self.logger.debug("'Boş doğrulama kodu' uyarısı kontrol edildi.")

        # Hatalı veya boş doğrulama kodu uyarısı alındıysa True, alınmadıysa False döndürür.
        if self.wrong_verification_code or self.empty_verification_code:
            self.logger.debug("Hatalı veya boş doğrulama kodu uyarısı alındı.")
            self.__class__.verification_error_value = True

        else:
            self.logger.debug("Hatalı veya boş doğrulama kodu uyarısı alınmadı.")
            self.__class__.verification_error_value = False

        return None

    # Doğrulama kodu giriş işlemini gerçekleştirir ve hataları kontrol eder.
    def __click_verification_code(self) -> None:

        """
        Doğrulama kodu giriş işlemini gerçekleştirir ve hataları kontrol eder.
        """

        @ErrorHandling.elementclickintercepted_error(logger = self.logger, emessage = "Doğrulama kodu giriş alanına tıklanamadı.", gmessage = "Doğrulama kodu giriş alanına tıklanamadı.", exit = True)
        def click_verification_code() -> None:

            self.verification_code_input.clear()
            self.logger.debug("Doğrulama kodu giriş alanına tıklanıyor.")
            self.verification_code_input.click()
            time.sleep(6)
            self.login_button.click()
            self.logger.debug("Doğrulama kodu giriş alanına tıklandı.")
            return None

        return click_verification_code()

    # Doğrulama kodu giriş işlemini gerçekleştirir ve hataları kontrol eder.
    def verification_and_login(self) -> None:
            
        """
        Doğrulama kodu giriş işlemini gerçekleştirir ve hataları kontrol eder.
        """
            
        a = 0

        while self.verification_error_value:
            
            self.logger.debug("Doğrulama kodu giriş işlemi gerçekleştiriliyor.")
            self.__click_verification_code()
            time.sleep(2)
            self.__get_verification_error_code()
            self.logger.debug("Doğrulama kodu giriş işlemi gerçekleştirildi.")
            a += 1

            if a == 15:
                self.logger.critical("Doğrulama kodu giriş işlemi birden fazla kez gerçekleştirilemedi.")
                self.logger.debug(f"Doğrulama kodu giriş işlemi deneme sayısı: {a}")
                self.logger.critical("Çıkış yapılıyor.")
                sys.exit()

        self.logger.debug(f"Doğrulama kodu giriş işlemi deneme sayısı: {a}")

        return None

    # Giriş yapma fonksiyonu.
    @staticmethod
    def login(browser: webdriver.Chrome) -> None:

        """
        BIST DataStore sitesine giriş yapma fonksiyonu.
        """

        G_logger = LoggerObjects.VM_TV_VEE_G_logger # VMTV-VEE-G: Veri Modülü - Tarihsel Veri - Veri Elde Etme - Giriş

        G_logger.debug("BIST DataStore giriş yapma modülü çalıştırıldı.")

        login = DSLogIn(browser)

        login.open_website(WebSites.datastore)

        login.get_webelements()

        time.sleep(1)

        login.enter_login_info()

        login.verification_and_login()

        G_logger.debug("BIST DataStore giriş yapma modülü başarılıyla tamamlandı.")

        return None

class DSFilter(SeleniumBase, DSFilterWebelements, DSProductFilterStrings):

    """
    DSFilter sınıfı, BIST Veri kütüphanesinden veri elde etme modülünde filtreleme işlemlerini gerçekleştirebilmek için gerekli olan yöntemleri
    ve değişkenleri içerir.
    """

    def __init__(self, browser: webdriver.Chrome) -> None:
        super().__init__(browser, LoggerObjects.DSF_logger)
        self.select = Select

    # Filtreleme işlemleri için gerekli ana web elementlerini elde eder.
    def get_main_webelements(self) -> None:
        
        """
        Filtreleme işlemi için gerekli ana web elementlerini alır ve döndürür.
        """
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "'Daha fazla yükle' butonu bulunamadı.", gmessage = "'Daha fazla yükle' butonu bulunamadı.", exit = True)
        def get_load_more_button() -> None:
                    
            self.__class__.button_load_more = WebDriverWait(self.browser, 4).until(EC.presence_of_element_located(self.button_load_more_tuple))
            self.logger.debug(f"'Daha fazla yükle' butonu webelementi elde edildi.")
            return None
                
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Filtreleme butonu bulunamadı.", gmessage = "Filtreleme butonu bulunamadı.", exit = True)
        def get_open_filter_button() -> None:
            
            self.__class__.button_open_filter = WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.button_open_filter_tuple))
            self.logger.debug(f"Filtreleme butonu webelementi elde edildi.")
            return None
        
        get_load_more_button()
        get_open_filter_button()
        
        return None
        
    # Filtreleme işlemleri için gerekli filtreleme web elementlerini elde eder.
    def get_filter_webelements(self) -> None:
        
        """
        Filtreleme işlemi için gerekli filtreleme web elementlerini alır ve döndürür.
        """
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Başlangıç tarihi aralığı giriş alanı bulunamadı.", gmessage = "Başlangıç tarihi aralığı giriş alanı bulunamadı.", exit = True)
        def get_start_date_input() -> None:
            
            self.__class__.start_date_input = WebDriverWait(self.browser, 4).until(EC.presence_of_element_located(self.start_date_input_tuple))
            self.logger.debug(f"Başlangıç tarihi aralığı giriş alanı webelementi elde edildi.")
            return None
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Bitiş tarihi aralığı giriş alanı bulunamadı.", gmessage = "Bitiş tarihi aralığı giriş alanı bulunamadı.", exit = True)
        def get_end_date_input() -> None:
            
            self.__class__.end_date_input = WebDriverWait(self.browser, 4).until(EC.presence_of_element_located(self.end_date_input_tuple))
            self.logger.debug(f"Bitiş tarihi aralığı giriş alanı webelementi elde edildi.")
            return None
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Filtreleme butonu bulunamadı.", gmessage = "Filtreleme butonu bulunamadı.", exit = True)
        def get_apply_filter_button() -> None:
            
            self.__class__.button_apply_filter = WebDriverWait(self.browser, 4).until(EC.presence_of_element_located(self.button_apply_filter_tuple))
            self.logger.debug("Filtreleme butonu bulundu.")
            return None
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Kategori butonu bulunamadı.", gmessage = "Kategori butonu bulunamadı.", exit = True)
        def get_category_button() -> None:
            
            self.__class__.button_category = WebDriverWait(self.browser, 4).until(EC.presence_of_element_located(self.button_category_tuple))
            self.logger.debug("Kategori butonu bulundu.")
            return None
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Abonelik butonu bulunamadı.", gmessage = "Abonelik butonu bulunamadı.", exit = True)
        def get_subscription_button() -> None:
            
            self.__class__.button_subscription = WebDriverWait(self.browser, 4).until(EC.element_to_be_clickable(self.button_subscription_tuple))
            self.logger.debug("Abonelik butonu bulundu.")
            return None
        
        get_start_date_input()
        get_end_date_input()
        get_apply_filter_button()
        get_category_button()
        get_subscription_button()
        
        return None
        
    # Tüm ürünleri yüklemek için "Daha fazla yükle" butonuna tıklar.
    def __load_all_products(self) -> None:

        """
        Tüm ürünleri yüklemek için "Daha fazla yükle" butonuna tıklar.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Tüm ürünler yüklenemedi.", exit = True)
        def load_more() -> None:

            a = 0
            self.logger.debug("Tüm ürünler yükleniyor.")
            button_text = self.button_load_more.text

            while button_text == "Daha fazla yükle":
                WebDriverWait(self.browser, 4).until(EC.element_to_be_clickable(self.button_load_more))
                self.button_load_more.click()
                button_text = self.button_load_more.text
                a += 1

            self.logger.debug(f"Tüm ürünler yüklendi.")
            self.logger.debug(f"'Daha fazla yükle' butonuna tıklanma sayısı: {a}")

            return None

        return load_more()

    # Filtreleme araçlarını açar.
    def open_filter(self) -> None:

        """
        Filtreleme araçlarını açar.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Filtreleme araçları açılamadı.", exit = True)
        def open_filter() -> None:

            z = 0

            self.logger.info("Filtreleme araçları açılıyor.")
            while not self.open_filter_error_value:

                try:
                    self.button_open_filter.click()
                    self.logger.debug("Filtreleme butonuna tıklandı.")
                    self.logger.info("Filtreleme araçları açıldı.")
                    self.__class__.open_filter_error_value = True
                
                except:
                    self.logger.debug("Filtreleme araçları açılamadı.")
                    self.__class__.open_filter_error_value = False

                z += 1
                if z == 5:
                    self.logger.critical("Filtreleme araçları birden fazla kez açılamadı.")
                    self.logger.debug(f"Filtreleme araçları açılma deneme sayısı: {z}")
                    self.logger.critical("Çıkış yapılıyor.")
                    sys.exit()

            self.logger.debug(f"Filtreleme araçları açılma deneme sayısı: {z}")
            return None

        return open_filter()

    # Filtre alanındaki tarih sütunlarını temizler.
    def clear_date_fields(self) -> None:

        """
        Tarih aralığı alanlarını temizler.
        """
        
        z = 0

        self.logger.info("Tarih aralığı alanları temizleniyor.")
        self.__class__.start_date_error_value = False
        self.__class__.end_date_error_value = False

        # Başlangıç tarihi alanını temizler.
        while not self.start_date_error_value:

            try:
                self.start_date_input.clear()
                self.__class__.start_date_error_value = True
                self.logger.debug("Başlangıç tarihi alanı temizlendi.")
                
            except:
                self.logger.debug("Başlangıç tarihi alanı temizlenemedi.")
                self.__class__.start_date_error_value = False

            z += 1
            if z == 5:
                self.logger.critical("Başlangıç tarihi alanı birden fazla kez temizlenemedi.")
                self.logger.critical("Çıkış yapılıyor.")
                sys.exit()

        # Bitiş tarihi alanını temizler.
        while not self.end_date_error_value:

            try:
                self.end_date_input.clear()
                self.__class__.end_date_error_value = True
                self.logger.debug("Bitiş tarihi alanı temizlendi.")
                
            except:
                self.logger.debug("Bitiş tarihi alanı temizlenemedi.")
                self.__class__.end_date_error_value = False

            z += 1
            if z == 5:
                self.logger.critical("Bitiş tarihi alanı birden fazla kez temizlenemedi. Web elementi bulunamadı.")
                self.logger.debug(f"Bitiş tarihi alanı temizlenme deneme sayısı: {z}")
                self.logger.critical("Çıkış yapılıyor.")
                sys.exit()

        self.logger.info("Tarih aralığı alanları temizlendi.")

        return None

    # Tarih aralığını belirler.
    def __date_filter(self, son_tarih: str) -> None:

        """
        Tarih aralığını belirler.
        """

        # Başlangıç tarihini belirler.        
        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Başlangıç tarihi aralığı giriş alanına veri girilemedi.", exit = True)
        def enter_start_date(son_tarih: str) -> None:
            
            self.start_date_input.click()
            self.logger.debug("Başlangıç tarihi alanına tıklandı.")
            self.start_date_input.send_keys(son_tarih)
            self.logger.debug(f"Başlangıç tarihi girildi. Tarih: {son_tarih}")
            time.sleep(1)
            return None
        
        # Bitiş tarhini belirler.
        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Bitiş tarihi aralığı giriş alanına veri girilemedi.", exit = True)
        def enter_end_date() -> None:

            self.end_date_input.click()
            self.logger.debug("Bitiş tarihi alanına tıklandı.")
            self.end_date_input.send_keys(datetime.strftime(datetime.now(), "%d-%m-%Y"))
            self.logger.debug(f"Bitiş tarihi girildi. Tarih: {datetime.strftime(datetime.now(), '%d-%m-%Y')}")
            self.logger.debug("Tarih aralığı belirlendi.")
            time.sleep(1)
            return None
                
        enter_start_date(son_tarih)
        enter_end_date()

        return None

    # Filtreleme butonuna tıklar.
    def __click_apply_filter_button(self) -> None:
            
        """
        Filtreleme butonuna tıklar.
        """

        @ErrorHandling.elementclickintercepted_error(logger = self.logger, emessage = "Filtreleme butonuna tıklanamadı.", gmessage = "Filtreleme butonuna tıklanamadı.", exit = True)
        def click_apply_filter_button() -> None:

            self.button_apply_filter.click()
            self.logger.debug("Filtreleme butonuna tıklandı.")
            time.sleep(1)
            return None

        return click_apply_filter_button()

    # Kategori butonuna tıklar.
    def __click_category_button(self) -> None:

        @ErrorHandling.elementclickintercepted_error(logger = self.logger, emessage = "Kategori butonuna tıklanamadı.", gmessage = "Kategori butonuna tıklanamadı.", exit = True)
        def click_category_button() -> None:
            
            self.button_category.click()
            self.logger.debug("Kategori butonuna tıklandı.")
            time.sleep(1)
            return None
        
        return click_category_button()

    # Abonelik butonuna tıklar.
    def __click_subscription_button(self) -> None:
            
        """
        Abonelik butonuna tıklar.
        """

        @ErrorHandling.elementclickintercepted_error(logger = self.logger, emessage = "Abonelik butonuna tıklanamadı.", gmessage = "Abonelik butonuna tıklanamadı.", exit = True)
        def click_subscription_button() -> None:

            self.button_subscription.click()
            self.logger.debug("Abonelik butonuna tıklandı.")
            time.sleep(1)
            return None

        return click_subscription_button()

    # Kategori filtresini kullanarak ürünleri filtreler.
    def __category_filter(self, category: str, group: str, sub_category: str, product_type: str) -> None:

        """
        Belirtilen ürünleri kategori filtresini kullanarak filtreler ve bu ürünler ile ilgili bilgileri listeler.
        """

        # Kategoriyi belirler.
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Kategori filtresi yüklenemedi.", gmessage = "Kategori filtresi yüklenemedi.", exit = True)
        def get_category_filter() -> None:

            self.__class__.select_category = self.select(WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.filter_category_tuple)))
            self.logger.debug("Kategori filtresi bulundu.")
            return None

        @ErrorHandling.nosuchelement_error(logger = self.logger, emessage = "Belirtilen kategori bulunmuyor.", gmessage = "Belirtilen kategori seçilemedi.", exit = True)
        def select_category(category: str) -> None:

            self.select_category.select_by_visible_text(category)
            self.logger.debug(f"Kategori seçildi. Kategori: {category}")
            time.sleep(1)
            return None

        # Ürün grubunu belirler.
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Grup filtresi yüklenemedi.", gmessage = "Grup filtresi yüklenemedi.", exit = True)
        def get_group_filter() -> None:

            self.__class__.select_group = self.select(WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.filter_group_tuple)))
            self.logger.debug("Grup filtresi bulundu.")
            return None
        
        @ErrorHandling.nosuchelement_error(logger = self.logger, emessage = "Belirtilen ürün grubu bulunmuyor.", gmessage = "Belirtilen ürün grubu seçilemedi.", exit = True)
        def select_group(group: str) -> None:

            self.select_group.select_by_visible_text(group)
            self.logger.debug(f"Ürün grubu seçildi. Grup: {group}")
            time.sleep(1)
            return None

        # Alt kategoriyi belirler.
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Alt kategori filtresi yüklenemedi.", gmessage = "Alt kategori filtresi yüklenemedi.", exit = True)
        def get_sub_category_filter() -> None:

            self.__class__.select_sub_category = self.select(WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.filter_sub_category_tuple)))
            self.logger.debug("Alt kategori filtresi bulundu.")
            return None

        @ErrorHandling.nosuchelement_error(logger = self.logger, emessage = "Belirtilen alt kategori bulunmuyor.", gmessage = "Belirtilen alt kategori seçilemedi.", exit = True)
        def select_sub_category(sub_category: str) -> None:

            self.select_sub_category.select_by_visible_text(sub_category)
            self.logger.debug(f"Alt kategori seçildi. Alt kategori: {sub_category}")
            time.sleep(1)
            return None

        # Ürün tipini belirler.
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Ürün tipi filtresi yüklenemedi.", gmessage = "Ürün tipi filtresi yüklenemedi.", exit = True)
        def get_product_type_filter() -> None:

            self.__class__.select_product_type = self.select(WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.filter_product_type_tuple)))
            self.logger.debug("Ürün tipi filtresi bulundu.")
            return None
        
        @ErrorHandling.nosuchelement_error(logger = self.logger, emessage = "Belirtilen ürün tipi bulunmuyor.", gmessage = "Belirtilen ürün tipi seçilemedi.", exit = True)
        def select_product_type(product_type: str) -> None:

            self.select_product_type.select_by_visible_text(product_type)
            self.logger.debug(f"Ürün tipi seçildi. Ürün tipi: {product_type}")
            time.sleep(1)
            return None

        get_category_filter()
        select_category(category)
        get_group_filter()
        select_group(group)
        get_sub_category_filter()
        select_sub_category(sub_category)
        get_product_type_filter()
        select_product_type(product_type)

        return None

    # Abonelik filtresini kullanarak ürünleri filtreler.
    def __subscription_filter(self, subscription: str) -> None:

        """
        Abonelik filtresini kullanarak ürünleri filtreler.
        """

        # Abonelik filtresini kullanarak ürünleri filtreler.
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Abonelik filtresi yüklenmedi.", gmessage = "Abonelik filtresi bulunamadı.", exit = True)
        def get_subscription_filter() -> None:

            self.__class__.select_subscription = self.select(WebDriverWait(self.browser, 6).until(EC.presence_of_element_located(self.filter_subscription_tuple)))
            self.logger.debug("Abonelik filtresi bulundu.")
            return None
        
        @ErrorHandling.nosuchelement_error(logger = self.logger, emessage = "Belirtilen abonelik bulunmuyor.", gmessage = "Belirtilen abonelik seçilemedi.", exit = True)
        def select_subscription(subscription: str) -> None:

            self.select_subscription.select_by_visible_text(subscription)
            self.logger.debug(f"Abonelik filtresi seçildi. Abonelik: {subscription}")
            time.sleep(1)
            return None

        get_subscription_filter()
        select_subscription(subscription)

        return None
        
    # Filtreleme işlemini gerçekleştirir.
    def __filter(self, category = None, group = None, sub_category = None, product_type = None, subscription = None, son_tarih = "01-08-2020") -> None:

        """
        İstenen niteliklere göre ürünleri filtreler ve bu ürünler
        ile ilgili bilgileri listeler.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Filtreleme işlemi tamamlanamadı.", exit = True)
        def filtreleme(category, group, sub_category, product_type, subscription, son_tarih) -> None:

            # Son tarih tipi None ise varsayılan olarak 01-08-2020 tarihini seçer.
            if son_tarih == None:
                self.logger.debug("Son tarih belirtilmedi. Varsayılan olarak 01-08-2020 tarihi seçildi.")
                son_tarih = "01-08-2020"

            # Filtreleme işlemini gerçekleştirir.
            self.logger.debug("Filtreleme işlemi başlatılıyor.")

            # Subscription argümanının değerine göre filtreleme işlemi gerçekleştirir.
            if subscription == None:
                self.logger.debug("Kategori filtresi kullanılarak ürünler filtreleniyor.")
                self.__click_category_button()
                self.__category_filter(category, group, sub_category, product_type)
            else:
                self.logger.debug("Abonelik filtresi kullanılarak ürünler filtreleniyor.")
                self.__click_subscription_button()
                self.__subscription_filter(subscription)

            # Tarih aralığını belirler.
            self.__date_filter(son_tarih)

            # Filtreleme butonuna tıklar.
            self.__click_apply_filter_button()

            # Tüm ürünleri yüklemek için "Daha fazla yükle" butonuna tıklar.
            self.__load_all_products()

            self.logger.debug("Filtreleme işlemi tamamlandı. Tüm ürünler başarıyla listelendi")

            return None
        
        return filtreleme(category, group, sub_category, product_type, subscription, son_tarih)

    # Ürün bazlı filtreleme metodları. !!!!filtreler ile ilgili filteleme değişkenleri düzenlenebilir.!!!!
    def ppgunsonufiyat(self, vt_obj: HistoricalDataModul) -> None:

        """
        Pay Piyasası Verileri kategorisindeki 'Gün Sonu Fiyat ve İşlem Hacmi Bilgileri' ürünlerini filtreler ve bu ürünler
        ile ilgili bilgileri listeler.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Pay Piyasası Gün Sonu Fiyat ve İşlem Hacmi Bilgileri ürünleri listelenemedi.", exit = True)
        def ppgunsonufiyat(vt_obj: HistoricalDataModul) -> None:

            # Filtreler
            self.logger.debug("Filtreler belirleniyor...")
            category = self.ppgunsonufiyat_dict["category"] # Kategori
            group = self.ppgunsonufiyat_dict["group"] # Grup
            sub_category = self.ppgunsonufiyat_dict["sub_category"] # Alt Kategori
            product_type = self.ppgunsonufiyat_dict["product_type"] # Ürün Tipi
            subscription = self.ppgunsonufiyat_dict["subscription"] # Abonelik
            self.logger.debug("Filtreler belirlendi.")

            # Fiyat veritabanındaki en son tarihi alır.
            son_tarih = vt_obj.get_latest_date(DatabaseTables.datastore_h_stock) 
        
            # Filtreleme işlemini gerçekleştirir.
            self.__filter(category, group, sub_category, product_type, subscription, son_tarih)

            return None

        return ppgunsonufiyat(vt_obj)

    def ppgunsonuendeks(self, vt_obj: HistoricalDataModul) -> None:

        """
        Pay Piyasası Verileri kategorisindeki 'Gün Sonu Endeks ve İşlem Hacmi Bilgileri' ürünlerini filtreler ve bu ürünler
        ile ilgili bilgileri listeler.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Pay Piyasası Gün Sonu Endeks ve İşlem Hacmi Bilgileri ürünleri listelenemedi.", exit = True)
        def ppgunsonuendeks(vt_obj: HistoricalDataModul) -> None:

            # Filtreler
            self.logger.debug("Filtreler belirleniyor...")
            category = self.ppgunsonuendeks_dict["category"] # Kategori
            group = self.ppgunsonuendeks_dict["group"] # Grup
            sub_category = self.ppgunsonuendeks_dict["sub_category"] # Alt Kategori
            product_type = self.ppgunsonuendeks_dict["product_type"] # Ürün Tipi
            subscription = self.ppgunsonuendeks_dict["subscription"] # Abonelik
            self.logger.debug("Filtreler belirlendi.")

            # Endeks veritabanındaki en son tarihi alır.
            son_tarih = vt_obj.get_latest_date(DatabaseTables.datastore_h_index) 
        
            # Filtreleme işlemini gerçekleştirir.
            self.__filter(category, group, sub_category, product_type, subscription, son_tarih)

            return None

        return ppgunsonuendeks(vt_obj)

    def cariendekshisse(self, vt_obj: HistoricalDataModul) -> None:

        """
        Endeks Verileri kategorisindeki 'Endeks Kapsamındaki Şirketler (Cari Durum)' ürünlerini filtreler ve bu ürünler
        ile ilgili bilgileri listeler.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Endeks Kapsamındaki Şirketler (Cari Durum) ürünleri listelenemedi.", exit = True)
        def cariendekshisse(vt_obj: HistoricalDataModul) -> None:

            # Filtreler
            self.logger.debug("Filtreler belirleniyor...")
            category = self.cariendekshisse_dict["category"] # Kategori
            group = self.cariendekshisse_dict["group"] # Grup
            sub_category = self.cariendekshisse_dict["sub_category"] # Alt Kategori
            product_type = self.cariendekshisse_dict["product_type"] # Ürün Tipi
            subscription = self.cariendekshisse_dict["subscription"] # Abonelik
            self.logger.debug("Filtreler belirlendi.")

            # Endeks Cari veritabanındaki en son tarihi alır.
            son_tarih = vt_obj.get_latest_date(DatabaseTables.datastore_c_stock_index) 
    
            # Filtreleme işlemini gerçekleştirir.
            self.__filter(category, group, sub_category, product_type, subscription, son_tarih)

            return None

        return cariendekshisse(vt_obj)

    def eskiendekshisse(self, vt_obj: HistoricalDataModul) -> None:

        """
        Endeks Verileri kategorisindeki '2000 Yılından İtibaren Endekslerde Bulunan Şirketler(BIST 30, BIST 50 ve BIST 100 için)' ürünlerini filtreler ve bu ürünler
        ile ilgili bilgileri listeler.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "2000 Yılından İtibaren Endekslerde Bulunan Şirketler ürünleri listelenemedi.", exit = True)
        def eskiendekshisse(vt_obj: HistoricalDataModul) -> None:

            # Filtreler
            self.logger.debug("Filtreler belirleniyor...")
            category = self.eskiendekshisse_dict["category"] # Kategori
            group = self.eskiendekshisse_dict["group"] # Grup
            sub_category = self.eskiendekshisse_dict["sub_category"] # Alt Kategori
            product_type = self.eskiendekshisse_dict["product_type"] # Ürün Tipi
            subscription = self.eskiendekshisse_dict["subscription"] # Abonelik
            self.logger.debug("Filtreler belirlendi.")

            # Eski Endeks veritabanındaki en son tarihi alır.
            son_tarih = vt_obj.get_latest_date(DatabaseTables.datastore_h_stock_index)

            # Filtreleme işlemini gerçekleştirir.
            self.__filter(category, group, sub_category, product_type, subscription, son_tarih)

            return None

        return eskiendekshisse(vt_obj)

    def endeksvolatilite(self, vt_obj: HistoricalDataModul) -> None:

        """
        Endeks Verileri Aboneliği kategorisindeki 'Endeks Volatilite Değerleri' ürünlerini filtreler ve bu ürünler
        ile ilgili bilgileri listeler.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Endeks Volatilite Değerleri ürünleri listelenemedi.", exit = True)
        def endeksvolatilite(vt_obj: HistoricalDataModul) -> None:

            # Filtreler
            self.logger.debug("Filtreler belirleniyor...")
            category = self.endeksvolatilite_dict["category"] # Kategori
            group = self.endeksvolatilite_dict["group"] # Grup
            sub_category = self.endeksvolatilite_dict["sub_category"] # Alt Kategori
            product_type = self.endeksvolatilite_dict["product_type"] # Ürün Tipi
            subscription = self.endeksvolatilite_dict["subscription"] # Abonelik
            self.logger.debug("Filtreler belirlendi.")

            # Endeks Volatilite veritabanındaki en son tarihi alır.
            son_tarih = vt_obj.get_latest_date(DatabaseTables.datastore_h_volatility) 
        
            # Filtreleme işlemini gerçekleştirir.
            self.__filter(category, group, sub_category, product_type, subscription, son_tarih)

            return None

        return endeksvolatilite(vt_obj)

    # Altta kalan metodlar FAZ-II için eklenmiştir. Henüz tamamlanmamıştır.

    def guniciendeks(self, vt_obj: HistoricalDataModul) -> None:
        pass

    def gunislemdefteri(self, vt_obj: HistoricalDataModul) -> None:
        pass

    def gunemirdefteri(self, vt_obj: HistoricalDataModul) -> None:
        pass

class DSDownload(SeleniumBase, DSDownloadWebelements):

    """
    DSDownload sınıfı, BIST DataStore sitesinden veri indirme işlemlerini gerçekleştirebilmek için gerekli değişken
    ve metodları içerir.
    """

    def __init__(self, browser: webdriver.Chrome) -> None:
        super().__init__(browser, LoggerObjects.VM_TV_VEE_I_logger)

    # İndirme işlemi için gerekli header webelementlerini elde eder.
    def __get_header_webelements(self) -> None:

        """
        İndirme işlemi için gerekli header webelementlerini elde eder.
        """

        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Ürün header webelementleri bulunamadı.", gmessage = "Ürün header webelementleri elde edilemedi.", exit = False)
        def get_header_webelements() -> None:

            self.__class__.product_item_header_webelements = None # Eğer önceden atanmış değer varsa değişkeni sıfırlar.
            self.__class__.product_item_header_webelements = WebDriverWait(self.browser, 6).until(EC.presence_of_all_elements_located(self.product_item_header_tuple))
            self.logger.debug("Ürün header webelementleri elde etme işlemi tamamlandı.")
            return None
        
        @ErrorHandling.timeout_error(logger = self.logger, emessage = "Ürün collapsed header webelementleri bulunamadı.", gmessage = "Ürün collapsed header webelementleri elde edilemedi.", exit = False)
        def get_collapsed_header_webelements() -> None:

            self.__class__.product_item_header_collapsed_webelements = None # Eğer önceden atanmış değer varsa değişkeni sıfırlar.
            self.__class__.product_item_header_collapsed_webelements = WebDriverWait(self.browser, 6).until(EC.presence_of_all_elements_located(self.product_item_header_collapsed_tuple))
            self.logger.debug("Ürün collapsed header webelementleri elde etme işlemi tamamlandı.")
            return None

        with ThreadPoolExecutor() as executor:
            
            collapsed_headers = executor.submit(get_collapsed_header_webelements)
            headers = executor.submit(get_header_webelements)
            
            wait([collapsed_headers, headers])

        return None

    # İndirme işlemi için gerekli açılamamış header web elementlerine tıklar.
    def __click_unopened_headers(self) -> None:
        
        """
        İndirme işlemi için gerekli açılamamış header web elementlerine tıklar.
        """
        
        if self.product_item_header_webelements == None:
            self.logger.debug("Header bulunamadı.")
            self.logger.debug("Çıkış yapılıyor.")
            return None
        
        try:
            headers_set = set(self.product_item_header_webelements)
        except:
            headers_set = set()
            
        try:
            opened_headers_set = set(self.product_item_header_collapsed_webelements)
        except:
            opened_headers_set = set()
            
        if opened_headers_set == set():
            unopened_headers = headers_set
        else:
            unopened_headers = headers_set - opened_headers_set
                
        self.logger.debug("Açılamamış headera tıklama işlemi başlatılıyor.")
        for li in self.sort_elements(unopened_headers):
            try:
                self.scroll_to_element(li)
                li.click()
            except ElementClickInterceptedException as e:
                self.logger.warning("Elemente tıklama işlemi engellendi. Headera tıklanamadı.")
                self.logger.debug(f"{e}")
            except Exception as e:
                self.logger.warning("Beklenmeyen bir hata oluştu. Headera tıklanamadı.")
                self.logger.debug(f"{e}")
                
        if unopened_headers:
            self.__class__.intercepted_value = True
        else:
            self.__class__.intercepted_value = False
            
        self.logger.debug("Açılamamış header tıklama işlemi tamamlandı.")
        return None
    
    # İndirme işlemi için gerekli header web elementlerine tıklar.
    def __click_headers(self) -> None:
        
        """
        İndirme işlemi için gerekli header web elementlerine tıklar ve açılmamış headerları açar.
        """

        self.__get_header_webelements()
        self.__click_unopened_headers()
        
        while self.intercepted_value:
        
            self.__get_header_webelements()
            self.__click_unopened_headers()
        
        return None
    
    # İndirme işlemi için gerekli dosya isimlerini ve linklerini istenen filtreye göre elde eder.
    def __get_download_infos(self, control_value: str = None) -> None:

        """
        İndirme işlemi için gerekli dosya isimlerini ve linklerini istenen filtreye göre elde eder.
        """

        def get_name_text(i) -> None:

            try:
                name = WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(self.get_name_webelement(i)))
                self.scroll_to_element(name)
                self.__class__.name_text = name.text
                self.__class__.name_error_value = True
                return None
            
            except Exception as e:
                self.logger.debug("Zaman aşımı. İndirme ismi bulunamadı.")
                self.logger.debug(f"{e}")
                self.__class__.name_error_value = False
                return None
        
        def get_link_text(i) -> None:

            try:
                link = WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(self.get_link_webelement(i)))
                self.__class__.link_text = link.get_attribute("href")
                self.__class__.link_error_value = True
                return None
            
            except Exception as e:
                self.logger.debug("Zaman aşımı. İndirme linki bulunamadı.")
                self.logger.debug(f"{e}")
                self.__class__.link_error_value = False
                return None

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "İndirme bilgileri elde edilemedi.", exit = True)
        def get_download_info(control_value: str = None) -> None:

            if self.product_item_header_webelements == None:
                self.logger.debug("İndirme bilgileri elde edilecek ürün bulunamadı.")
                return None

            i = 1
            self.logger.debug("İndirme bilgileri elde ediliyor...")
            while i <= len(self.product_item_header_webelements):

                z = 1
                self.__class__.name_error_value = False
                self.__class__.link_error_value = False

                # İndirme isimlerini elde eder.
                while not self.name_error_value:

                    get_name_text(i)
                    z += 1

                    if z == 5:
                        self.logger.critical("İndirme ismi birden fazla kez elde edilemedi.")
                        self.logger.debug(f"İndirme ismi elde etme deneme sayısı: {z}")
                        self.logger.critical("İndirme bilgilerini elde etme işlemi iptal edildi.")
                        time.sleep(30)
                        sys.exit()
                
                # İndirme linklerini elde eder.
                while not self.link_error_value:

                    get_link_text(i)
                    z += 1

                    if z == 5:
                        self.logger.critical("İndirme linki birden fazla kez elde edilemedi.")
                        self.logger.debug(f"İndirme linki elde etme deneme sayısı: {z}")
                        self.logger.critical("İndirme bilgilerini elde etme işlemi iptal edildi.")
                        time.sleep(30)
                        sys.exit()

                # İndirme isimlerini ve linklerini kontrol eder ve belirtilen filtreye göre bir dicte ekler. Default filtre değeri None'dir.
                if control_value == None:
                    self.__class__.download_names.append(self.name_text)
                    self.__class__.download_links.append(self.link_text)
                    self.logger.debug(f"{self.name_text} adlı dosyanın indirme bilgileri listeye eklendi.")
                    
                else:
                    if control_value in self.name_text:
                        self.__class__.download_names.append(self.name_text)
                        self.__class__.download_links.append(self.link_text)
                        self.logger.debug(f"{self.name_text} adlı dosyanın indirme bilgileri listeye eklendi.")
                        
                i += 1

            self.logger.debug("İndirme bilgileri elde edildi.")

            return None

        self.__click_headers()
        
        get_download_info(control_value)

        return None

    # Dosya indirme işlemini gerçekleştirir.
    def __download_files(self) -> None:

        """
        Dosya indirme işlemini gerçekleştirir.
        """

        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Dosya indirme işlemi tamamlanamadı.", exit = True)
        def download_files() -> None:
            
            i = 0
            
            # İndirme işlemi başlamadan önce indirme klasöründeki .crdownload uzantılı dosyaları siler.
            incomplete_downloads = [filename for filename in os.listdir(Paths.indirme_dir) if filename.endswith('.crdownload')]
            if incomplete_downloads != []:
                for filename in incomplete_downloads:
                    os.remove(os.path.join(Paths.indirme_dir, filename))
                self.logger.debug("İndirme klasöründe halihazırda bulunan .crdownload uzantılı dosyalar silindi.")

            if self.download_names == None:
                self.logger.debug("İndirme bilgileri bulunamadı.")
                self.logger.debug("Çıkış yapılıyor.")
                return None

            self.logger.debug("Dosya indirme işlemi başlatılıyor...")
            while i < len(self.download_names):
                self.logger.debug(f"{self.download_names[i]} adlı dosya indiriliyor...")
                self.browser.get(self.download_links[i])
                i += 1
            self.logger.debug("Dosya indirme işlemi tamamlandı.")

            return None

        return download_files()

    # İndirme işlemlerini kontrol eder.
    def __download_control(self) -> None:

        """
        Tarayıcıdan indirilen dosyaların tamamlanıp tamamlanmadığını kontrol eder.
        """
        
        @ErrorHandling.unexpected_error(logger = self.logger, gmessage = "Dosya indirme işlemleri tamamlanamadı.", exit = True)
        def download_control() -> None:

            self.logger.debug("İndirme işlemleri tamamlanıp tamamlanmadığı kontrol ediliyor.")
            
            time.sleep(5) # İndirme işlemlerinin tamamlanıp tamamlanmadığını kontrol etmeden önce 5 saniye bekle
            countd = 0
            incomplete_downloads = [filename for filename in os.listdir(Paths.indirme_dir) if filename.endswith('.crdownload')]
            
            while incomplete_downloads != []:
                time.sleep(1)  # Her bir kontrol arası 1 saniye bekle
                incomplete_downloads = [filename for filename in os.listdir(Paths.indirme_dir) if filename.endswith('.crdownload')]
                countd += 1
                if countd == 300: # 5 dakika bekler ve dosyaların indirilip indirilmediğini kontrol eder.
                    self.logger.error("Dosyaların indirmelerinin tamamlanması esnasında bir sorun oluştu.")
                    break
                    
            self.__class__.download_links.clear()
            self.__class__.download_names.clear()
            self.logger.debug("İndirme değişkenleri sıfırlandı.")
                    
            self.logger.debug("İndirme işlemleri tamamlandı.")

            return None
        
        return download_control()

    # İndirme işlemlerini gerçekleştirir.
    @staticmethod
    def download(browser: webdriver.Chrome, filter_value: str = None) -> None:

        """
        İndirme işlemlerini gerçekleştiren fonksiyon.
        """

        I_logger = LoggerObjects.VM_TV_VEE_I_logger

        @ErrorHandling.unexpected_error(logger = I_logger, gmessage = "İndirme modülü tamamlanamadı.", exit = True)
        def download(browser: webdriver.Chrome, filter_value: str = None) -> None:

            I_logger.debug("İndirme modülü başlatıldı.")

            # İndirme işlemleri sınıfından bir nesne oluşturur.
            indirme_bilgileri = DSDownload(browser) 

            # İndirme işlemi için gerekli bilgileri alır.
            indirme_bilgileri.__get_download_infos(filter_value)

            # İndirme işlemi yapılır.
            indirme_bilgileri.__download_files()
            
            # İndirme işlemlerini kontrol eder.
            indirme_bilgileri.__download_control()

            I_logger.debug("İndirme modülü tamamlandı.")

            return None
        
        return download(browser, filter_value)

class DSAcquisition:

    """
    DSAcquisition sınıfı, DataStore sitesinden veri çekme işlemlerini gerçekleştirir.
    """

    @staticmethod
    def VM_TV_VEE():

        """
        Tarihsel Veri - Elde Etme fonksiyonu. Bu fonksiyon, BIST Veri kütüphanesine giriş yapar,
        BIST Veri kütüphanesinden tarihsel verileri indirir ve ilgili klasöre kaydeder.
        """
       
        VEE_logger = LoggerObjects.VM_TV_VEE_logger # VM_TV_VEE: Veri Modülü - Tarihsel Veri - Veri Elde Etme

        @ErrorHandling.unexpected_error(logger = VEE_logger, gmessage = "Tarihsel Veri - Elde Etme fonksiyonu tamamlanamadı.", exit = True)
        def VM_TV_VEE():

            VEE_logger.info("Tarihsel Veri Elde Etme modülü başlatıldı.")

            VEE_logger.info("Tarayıcı başlatılıyor...")
            options = webdriver.ChromeOptions()
            options.add_experimental_option("prefs", Paths.prefs_indirme)
            browser = webdriver.Chrome(options=options)
            browser.maximize_window()
            VEE_logger.info("Tarayıcı başlatıldı.")

            # Veritabanı işlemleri
            VEE_logger.info("Veritabanı işlemleri başlatıldı.")
            HD_engine = create_engine(conn_string(DatabaseNames.finansal)) # Veritabanı bağlantısı. HD_Engine: Historical Data - Engine.
            metadata = MetaData()

            finansal_veritabani = HistoricalDataModul(HD_engine, metadata)

            VEE_logger.info("Veritabanı işlemleri tamamlandı.")

            # Ana program işlemleri
            VEE_logger.info("Ana program işlemleri başlatıldı.")

            VEE_logger.info("Giriş işlemi başlatılıyor.")
            DSLogIn.login(browser)
            VEE_logger.info("Giriş işlemi tamamlandı.")

            time.sleep(2) # Sayfanın yüklenmesi için 2 saniye bekle

            # Filtreleme modülü
            filtreleme = DSFilter(browser)
            VEE_logger.info("Filtreleme ve indirme modülleri başlatılıyor.")
            filtreleme.get_main_webelements()
            
            filtreleme.open_filter()
            
            filtreleme.get_filter_webelements()

            #Günsonu Fiyat Hacim filtreleme ve indirme modülü
            VEE_logger.info("Günsonu Fiyat Hacim filtreleme işlemi başlatılıyor.")
            filtreleme.ppgunsonufiyat(vt_obj= finansal_veritabani)
            VEE_logger.info("Günsonu Fiyat Hacim filtreleme işlemi tamamlandı.")

            VEE_logger.info("Veri indirme işlemi başlatılıyor.")
            DSDownload.download(browser)

            filtreleme.clear_date_fields()

            #Günsonu Endeks Hacim filtreleme ve indirme modülü
            VEE_logger.info("Filtreleme işlemi başlatılıyor.")
            filtreleme.ppgunsonuendeks(vt_obj= finansal_veritabani)
            VEE_logger.info("Filtreleme işlemi tamamlandı.")

            VEE_logger.info("Veri indirme işlemi başlatılıyor.")
            DSDownload.download(browser)

            filtreleme.clear_date_fields()

            #2000 Yılından İtibaren Endekslerde Bulunan Şirketler(BIST 30, BIST 50 ve BIST 100 için) filtreleme ve indirme modülü
            VEE_logger.info("2000 Yılından İtibaren Endekslerde Bulunan Şirketler(BIST 30, BIST 50 ve BIST 100 için) filtreleme işlemi başlatılıyor.")
            filtreleme.eskiendekshisse(vt_obj= finansal_veritabani)
            VEE_logger.info("2000 Yılından İtibaren Endekslerde Bulunan Şirketler(BIST 30, BIST 50 ve BIST 100 için) filtreleme işlemi tamamlandı.")

            VEE_logger.info("Veri indirme işlemi başlatılıyor.")
            DSDownload.download(browser)

            VEE_logger.info("Veri indirme işlemleri tamamlandı.")

            VEE_logger.info("Tarayıcı kapatılıyor.")
            browser.quit()
            VEE_logger.info("Tarayıcı kapatıldı.")

            VEE_logger.info("Veri Elde Etme modülü tamamlandı.")

            return None

        return VM_TV_VEE()

    @staticmethod
    def VM_EVG_VEE():

        """
        Endeks Verileri Güncelleme - Veri Elde Etme fonksiyonu. Bu fonksiyon, BIST Veri kütüphanesine giriş yapar,
        BIST Veri kütüphanesinden endeks verilerini indirir ve ilgili klasöre kaydeder.
        """

        VEE_logger = LoggerObjects.VM_EVG_VEE_logger # VM_EVG_VEE: Veri Modülü - Endeks Verileri Getirme - Veri Elde Etme

        @ErrorHandling.unexpected_error(logger = VEE_logger, gmessage = "Endeks Verileri Güncelleme modülü tamamlanamadı.", exit = True)
        def VM_EVG_VEE():

            VEE_logger.info("Endeks Verileri Güncelleme modülü başlatıldı.")

            VEE_logger.info("Tarayıcı başlatılıyor...")
            options = webdriver.ChromeOptions()
            options.add_experimental_option("prefs", Paths.prefs_indirme)
            browser = webdriver.Chrome(options=options)
            browser.maximize_window()
            VEE_logger.info("Tarayıcı başlatıldı.")


            # Veritabanı işlemleri
            VEE_logger.info("Veritabanı işlemleri başlatıldı.")
            HD_engine = create_engine(conn_string(DatabaseNames.finansal)) # Veritabanı bağlantısı. HD_Engine: Historical Data - Engine.
            metadata = MetaData()
            
            finansal_veritabani = HistoricalDataModul(HD_engine, metadata)

            VEE_logger.info("Veritabanı işlemleri tamamlandı.")

            # Veri Elde Etme işlemleri
            VEE_logger.info("Ana program işlemleri başlatıldı.")

            DSLogIn.login(browser)

            time.sleep(2) # Sayfanın yüklenmesi için 2 saniye bekle

            # Filtreleme nesnesi oluşturulur.
            filtreleme = DSFilter(browser)
            
            filtreleme.get_main_webelements()
            
            filtreleme.open_filter()

            filtreleme.get_filter_webelements()

            #Endeks Kapsamındaki Şirketler (Cari Durum) filtreleme ve indirme modülü
            VEE_logger.info("Endeks Kapsamındaki Şirketler (Cari Durum) filtreleme işlemi başlatılıyor.")
            filtreleme.cariendekshisse(vt_obj= finansal_veritabani)
            VEE_logger.info("Endeks Kapsamındaki Şirketler (Cari Durum) filtreleme işlemi tamamlandı.")

            VEE_logger.info("Veri indirme işlemi başlatılıyor.")
            DSDownload.download(browser)

            filtreleme.clear_date_fields()

            #BIST Volatilite Endeks Değerleri filtreleme ve indirme modülü
            VEE_logger.info("BIST Volatilite Endeks Değerleri filtreleme işlemi başlatılıyor.")
            filtreleme.endeksvolatilite(vt_obj= finansal_veritabani)
            VEE_logger.info("BIST Volatilite Endeks Değerleri filtreleme işlemi tamamlandı.")

            VEE_logger.info("Veri indirme işlemi başlatılıyor.")
            DSDownload.download(browser, DSProductFilterStrings.endeksvolatilite_dict["filter_value"])

            VEE_logger.info("Veri indirme işlemleri tamamlandı.")

            VEE_logger.info("Tarayıcı kapatılıyor.")
            browser.quit()
            VEE_logger.info("Tarayıcı kapatıldı.")

            VEE_logger.info("Endeks Verileri Güncelleme modülü tamamlandı.")

            return None

        return VM_EVG_VEE()

if __name__ == "__main__":

    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", Paths.prefs_indirme)
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()

    DSLogIn.login(browser)
    """
    
    #DSAcquisition.VM_TV_VEE()
    DSAcquisition.VM_EVG_VEE()
    print("Çıkış yapılıyor.")
    sys.exit()
    