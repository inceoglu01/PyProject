import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

from webautomation import SeleniumWebAutomationBase, SeleniumWebScrappingBase

from logging import Logger as _Logger
import selenium.webdriver as webdriver

# Web otomasyon ve webscrapping işlemlerinde kullanılan ana sınıflar.
class LogInBase(SeleniumWebAutomationBase):

    """
    LogIn sınıfı, veri sitelerine giriş yapma işlemlerini gerçekleştirebilmek için gerekli değişken ve metodları içerir.
    """

    # LogIn sınıfının yapıcı metodunu oluşturur.
    def __init__(self, browser: webdriver.Chrome, logger: _Logger) -> None:
        super().__init__(browser, logger)

class MainWindowBase(SeleniumWebAutomationBase, SeleniumWebScrappingBase):

    """
    MainWindow sınıfı, veri sitelerindeki ana sayfaları temsil eder.
    """

    # MainWindow sınıfının yapıcı metodunu oluşturur.
    def __init__(self, browser: webdriver.Chrome, logger: _Logger) -> None:
        super().__init__(browser, logger)

class AcquisitionBase(SeleniumWebAutomationBase, SeleniumWebScrappingBase):

    """
    Acquisition sınıfı, veri sitelerinden veri çekme işlemlerini gerçekleştirebilmek için gerekli değişken ve metodları içerir.
    """

    # Acquisition sınıfının yapıcı metodunu oluşturur.
    def __init__(self, browser: webdriver.Chrome, logger: _Logger) -> None:
        super().__init__(browser, logger)
        
    # Ortak veri elede etme sınıfı.
    def get_data(self) -> None:
        pass

if __name__ == "__main__":

    pass
