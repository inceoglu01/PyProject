import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

import time as _time
from selenium.webdriver.remote.webelement import WebElement as _WebElement
from selenium.webdriver.support.ui import WebDriverWait as _WebDriverWait
from selenium.webdriver.support import expected_conditions as _EC
from selenium.webdriver import Chrome as _Chrome
import selenium.webdriver as _webdriver
from errorhandling import SeleniumErrorHandling
from logging import Logger as _Logger
from loggingmodule import LoggerObjects as _LoggerObjects

"""
Web otomasyon ve webscrapping işlemlerinde kullanılan ana sınıflar ve fonksiyonlar.
"""

class SeleniumWebBrowser:
    
    """
    Selenium web tarayıcısı sınıfı.
    """
    
    def __init__(self, prefs: str) -> None:
        self.prefs = prefs
        self.options = _webdriver.ChromeOptions()
        self.options.add_experimental_option("prefs", self.prefs)
        self.browser = _Chrome(options = self.options)
        
    def get_browser(self) -> _Chrome:
        self.browser.maximize_window()
        return self.browser
    
class SeleniumWebElementAttributes:
    
    """
    Selenium webelement attribute değişkenlerini içerir.
    
    Attribute sorgularında kullanılır.
    """
    
    text = "text"
    tag_name = "tag_name"
    size = "size"
    location = "location"
    rect = "rect"
    is_displayed = "is_displayed"
    is_enabled = "is_enabled"
    is_selected = "is_selected"

# Baz sınıflar.
class SeleniumBase:
    
    def __init__(self, browser: _Chrome, logger: _Logger) -> None:
        self.browser = browser
        self.logger = logger
    
    # İstenen web elementi elde eder.
    @SeleniumErrorHandling.nosuchelement_error(logger = _LoggerObjects.SB_logger, emessage= "None değeri döndürülüyor...", gmessage = "Webelement elde edilemedi.", exit = False)
    def find_element(self, selector: str, value: str | None) -> _WebElement:

        """
        İstenen web elementi elde eder. 
        
        Hata durumunda hata mesajı döndürür. Programdan çıkış yapmaz.
        """

        return self.browser.find_element(selector, value)
    
    # İstenen web elementlerini elde eder.
    @SeleniumErrorHandling.nosuchelement_error(logger = _LoggerObjects.SB_logger, emessage= "None değeri döndürülüyor...", gmessage = "Webelementler elde edilemedi.", exit = False)
    def find_elements(self, selector: str, value: str | None) -> list[_WebElement]:
        
        """
        İstenen web elementlerini elde eder.
        """
                    
        return self.browser.find_elements(selector, value)
        
    # İstenen web element bulunana kadar bekler.
    @SeleniumErrorHandling.timeout_error(logger = _LoggerObjects.SB_logger, emessage= "Webelement elde edilemedi.", gmessage = "Webelement bulunana kadar beklenirken hata oluştu.", exit = False)
    def wait_for_element(self, selector: str, value: str | None, timeout: int = 10) -> _WebElement:
        
        """
        İstenen web element bulunana kadar bekler.
        """
        
        return _WebDriverWait(self.browser, timeout).until(_EC.presence_of_element_located((selector, value)))
   
    # İstenen web elementler bulunana kadar bekler.
    @SeleniumErrorHandling.timeout_error(logger = _LoggerObjects.SB_logger, emessage= "Webelementler elde edilemedi.", gmessage = "Webelementler bulunana kadar beklenirken hata oluştu.", exit = False)
    def wait_for_elements(self, selector: str, value: str | None, timeout: int = 10) -> list[_WebElement]:
        
        """
        İstenen web elementler bulunana kadar bekler.
        """
        
        return _WebDriverWait(self.browser, timeout).until(_EC.presence_of_all_elements_located((selector, value)))
        
class SeleniumWebAutomationBase(SeleniumBase):
    
    # Web sitesine giriş yapar.
    @SeleniumErrorHandling.webdriver_error(logger = _LoggerObjects.SAB_logger, emessage= "Siteye giriş yapılamadı.", gmessage = "Siteye giriş yapılamadı.", exit = True)
    def open_website(self, url: str) -> None:

        """
        Web sitesine giriş yapar.
        """
        self.logger.debug("Siteye giriş yapılıyor...")
        self.browser.get(url)
        _time.sleep(1)
        self.logger.debug("Siteye giriş yapıldı.")
        return None
    
    # Verilen webelemente kaydırma işlemi yapar.
    @SeleniumErrorHandling.javascript_error(logger = _LoggerObjects.SWB_logger, emessage = "Webelemente kaydırma işlemi yapılamadı.", gmessage = "Webelemente kaydırma işlemi yapılamadı.", exit = False)
    def scroll_to_element(self, element: _WebElement) -> None:

        """
        Verilen webelemente kaydırma işlemi yapar.
        """

        self.browser.execute_script("arguments[0].scrollIntoView();", element)

        return None

    # Belirtilen butona tıklar.
    @SeleniumErrorHandling.elementclickintercepted_error(logger = _LoggerObjects.SWB_logger, emessage = "Butona tıklanamadı.", gmessage = "Butona tıklanamadı.", exit = False)
    def click(self, element: _WebElement) -> None:

        """
        Belirtilen butona tıklar.
        """

        element.click()

        return None

    # Belirtilen ögedeki metni temizler.
    @SeleniumErrorHandling.elementnotinteractable_error(logger = _LoggerObjects.SWB_logger, emessage = "Metin temizlenemedi.", gmessage = "Metin temizlenemedi.", exit = False)
    def clear(self, element: _WebElement) -> None:
            
        """
        Belirtilen ögedeki metni temizler.
        """

        element.clear()

        return None

    # Belirtilen elemente metin gönderir.
    @SeleniumErrorHandling.elementnotinteractable_error(logger = _LoggerObjects.SWB_logger, emessage = "Elemente metin gönderilemedi.", gmessage = "Elemente metin gönderilemedi.", exit = False)
    def send_keys(self, element: _WebElement, text: str) -> None:
        
        """
        Belirtilen elemente metin gönderir.
        """

        element.send_keys(text)

        return None

    # Belirtilen pencereye geçiş yapar.
    @SeleniumErrorHandling.window_error(logger = _LoggerObjects.SWB_logger, emessage = "Pencereye geçiş yapılamadı.", gmessage = "Pencereye geçiş yapılamadı.", exit = False)
    def switch_to_window(self, window: str) -> None:
            
        """
        Belirtilen pencereye geçiş yapar.
        """
        
        self.browser.switch_to.window(window)

        return None

    # Ana pencereye geçiş yapar.
    @SeleniumErrorHandling.window_error(logger = _LoggerObjects.SWB_logger, emessage = "Ana pencereye geçiş yapılamadı.", gmessage = "Ana pencereye geçiş yapılamadı.", exit = False)
    def switch_to_main_window(self) -> None:
            
        """
        Ana pencereye geçiş yapar.
        """

        self.browser.switch_to.window(self.browser.window_handles[0])

        return None

    # Belirtilen pencereyi kapatır.
    @SeleniumErrorHandling.window_error(logger = _LoggerObjects.SWB_logger, emessage = "Pencere kapatılamadı.", gmessage = "Pencere kapatılamadı.", exit = False)
    def close_window(self, window: str) -> None:
        
        """
        Belirtilen pencereyi kapatır.
        """
                
        self.browser.switch_to.window(window)
        self.browser.close()

        return None

    # Tarayıcıda yeni bir pencere açar.!!!!
    @SeleniumErrorHandling.window_error(logger = _LoggerObjects.SWB_logger, emessage = "Yeni pencere açılamadı.", gmessage = "Yeni pencere açılamadı.", exit = False)
    def open_new_window(self, url: str) -> None:
        
        """
        Tarayıcıda yeni bir pencere açar.
        """
        
        self.browser.execute_script("window.open();")
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.browser.get(url)

        return None
    
class SeleniumWebScrappingBase(SeleniumBase):

    """
    Webelementlere ilişkin genel değişkenleri ve genel metodları içerir.
    """

    # Webelemenleri attributelarına göre sıralar.
    @SeleniumErrorHandling.webdriver_error(logger = _LoggerObjects.SAB_logger, emessage= "Webelementler sıralanamadı.", gmessage = "Webelementler sıralanamadı.", exit = False)
    def sort_elements(self, elements: set[_WebElement] | list[_WebElement], by: str = SeleniumWebElementAttributes.text) -> list[_WebElement]:
        
        """
        Webelementleri attributelarına göre sıralar.
        """
        if isinstance(elements, set):
            elements = list(elements)
        elif isinstance (elements, list):
            pass
        else:
            raise TypeError("Webelementler listesi veya seti olmalıdır.")
        
        if by not in SeleniumWebElementAttributes.__dict__.values():
            raise ValueError("Geçersiz bir attribute değeri girildi.")
            
        if by == SeleniumWebElementAttributes.text:
            return sorted(elements, key = lambda x: x.text)
        elif by == SeleniumWebElementAttributes.tag_name:
            return sorted(elements, key = lambda x: x.tag_name)
        elif by == SeleniumWebElementAttributes.size:
            return sorted(elements, key = lambda x: x.size["width"] * x.size["height"])
        elif by == SeleniumWebElementAttributes.location:
            return sorted(elements, key = lambda x: x.location["x"] * x.location["y"])
        elif by == SeleniumWebElementAttributes.rect:
            return sorted(elements, key = lambda x: x.rect["width"] * x.rect["height"])
        elif by == SeleniumWebElementAttributes.is_displayed:
            return sorted(elements, key = lambda x: x.is_displayed())
        elif by == SeleniumWebElementAttributes.is_enabled:
            return sorted(elements, key = lambda x: x.is_enabled())
        elif by == SeleniumWebElementAttributes.is_selected:
            return sorted(elements, key = lambda x: x.is_selected())
        else:
            return elements

    # Websitesini HTML formatında döndürür.
    @SeleniumErrorHandling.webdriver_error(logger = _LoggerObjects.SAB_logger, emessage= "Websitesinin kaynağı indirilemedi.", gmessage = "Websitesi HTML formatında döndürülemedi.", exit = False)
    def get_page_source(self) -> str:

        """
        Websitesini HTML formatında döndürür.
        """

        html = self.browser.page_source

        return html

    # Webelementin attribute değerini döndürür.
    @SeleniumErrorHandling.attribute_error(logger = _LoggerObjects.SAB_logger, emessage= "Webelementin attribute değeri döndürülemedi.", gmessage = "Webelementin attribute değeri döndürülemedi.", exit = False)
    def get_attribute(self, element: _WebElement, attribute: str) -> str:
        
        """
        Webelementin attribute değerini döndürür.
        """
        
        if isinstance(element, _WebElement):
            pass
        else:
            raise TypeError("Element webelement olmalıdır.")
                
        if attribute == SeleniumWebElementAttributes.text:
            return element.text
        elif attribute == SeleniumWebElementAttributes.tag_name:
            return element.tag_name
        elif attribute == SeleniumWebElementAttributes.size:
            return element.size
        elif attribute == SeleniumWebElementAttributes.location:
            return element.location
        elif attribute == SeleniumWebElementAttributes.rect:
            return element.rect
        elif attribute == SeleniumWebElementAttributes.is_displayed:
            return element.is_displayed()
        elif attribute == SeleniumWebElementAttributes.is_enabled:
            return element.is_enabled()
        elif attribute == SeleniumWebElementAttributes.is_selected:
            return element.is_selected()
        else:
            return element.get_attribute(attribute)
