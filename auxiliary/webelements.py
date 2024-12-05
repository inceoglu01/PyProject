from selenium.webdriver.remote.webelement import WebElement as _WebElement
from selenium.webdriver.common.by import By as _By
from lxml.etree import _Element as _Element
import numpy as np

"""
Web otomasyon ve webscrapping işlemlerinde kullanılan webelement değişkenlerini ve metodlarını içerir.
"""

############################################################################################
# <!--- Webelementlerin tanımlanması ve değişkenlerin oluşturulması ---!>
# Webelementler zamanla değişebileceği için bu değişkenlerin harici bir dosya
# içerisinde tanımlanması ve ilgili değişkenin buradan güncellenmesi gerekmektedir.
# Bu işlem ile ilgili bir arayüz tasarlanabilir. Bu sürecin nasıl işleyeceği
# daha ayrıntılı araştırılmalıdır.
############################################################################################

# DataStore webelement listesi.
class DSLogInWebelements:
    
    """
    DataStore sitesine giriş yapmak için kullanılan webelement değişkenlerini içerir.
    """
    
    login_email_input_tuple = (_By.XPATH, "/html/body/div/div[1]/div/section/div[1]/div/div[2]/input")
    login_password_input_tuple = (_By.XPATH, "/html/body/div/div[1]/div/section/div[1]/div/div[3]/input")
    login_verification_code_input_tuple = (_By.XPATH, "/html/body/div/div[1]/div/section/div[1]/div/div[5]/div[3]/div/input")
    login_button_tuple = (_By.XPATH, "/html/body/div/div[1]/div/section/div[1]/div/div[6]/div[2]/button")
    login_wrong_verification_code_tuple = (_By.XPATH, "/html/body/div/div[1]/div/section/div[1]/div/small")
    login_empty_verification_code_tuple = (_By.XPATH, "/html/body/div/div[1]/div/section/div[1]/div/div[5]/div[3]/div/small")
    
    email_input = None
    password_input = None
    verification_code_input = None
    login_button = None
    
    wrong_code_webelement = None
    empty_code_webelement = None
    wrong_verification_code = None
    empty_verification_code = None
    
    login_error_value = True
    verification_error_value = True
    
class DSFilterWebelements:
    
    """
    DataStore sitesinde filtreleme işlemleri için kullanılan webelement değişkenlerini içerir.
    """
    
    open_filter_error_value = False
    start_date_error_value = False
    end_date_error_value = False
    
    button_load_more_tuple = (_By.CLASS_NAME, "load-more")
    button_load_more = None

    start_date_input_tuple = (_By.XPATH, "/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[2]/div/div/div/div[2]/input")
    end_date_input_tuple = (_By.XPATH, "/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[2]/div/div/div/div[3]/input")
    start_date_input = None
    end_date_input = None

    button_open_filter_tuple = (_By.XPATH, "/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[3]/a")
    button_open_filter = None
    
    button_apply_filter_tuple = (_By.XPATH, "/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[2]/div/div/div/div[6]/a")
    button_apply_filter = None
    
    button_subscription_tuple = (_By.XPATH, "/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[2]/div/div/div/div[1]/ul/li[2]/a")
    button_subscription = None
    
    button_category_tuple = (_By.XPATH, "/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[2]/div/div/div/div[1]/ul/li[1]/a")
    button_category = None

    filter_category_tuple = (_By.ID, "category-select")
    select_category = None
    
    filter_group_tuple = (_By.ID, "group-select")
    select_group = None
    
    filter_sub_category_tuple = (_By.ID, "subcategory-select")
    select_sub_category = None
    
    filter_product_type_tuple = (_By.ID, "product-type-select")
    select_product_type = None
    
    filter_subscription_tuple = (_By.ID, "subscription-select")
    select_subscription = None

class DSProductFilterStrings:
    
    """
    DataStore sitesinde filtreleme işlemleri için kullanılan string değişkenlerini içerir.
    """

    ppgunsonufiyat_dict = {"category": "Pay Piyasası", "group": "Pay Piyasası Verileri", 
                        "sub_category": "Gün Sonu Fiyat ve İşlem Hacmi Bilgileri", "product_type": "Gün Sonu Fiyat ve İşlem Hacmi Bilgileri",
                        "subscription": None, "filter_value": None}
    
    ppgunsonuendeks_dict = {"category": "Pay Piyasası", "group": "Pay Piyasası Verileri",
                          "sub_category": "Gün Sonu Endeks ve İşlem Hacmi Bilgileri", "product_type": "Gün Sonu Endeks ve İşlem Hacmi Bilgileri",
                          "subscription": None, "filter_value": None}
    
    cariendekshisse_dict = {"category": "Endeks Verileri", "group": "Endeks Verileri",
                          "sub_category": "Endeks Verileri", "product_type": "Endeks Kapsamındaki Şirketler (Cari Durum)",
                          "subscription": None, "filter_value": None}
    
    eskiendekshisse_dict = {"category": "Endeks Verileri", "group": "Endeks Verileri",
                            "sub_category": "Endeks Verileri", "product_type": "2000 Yılından İtibaren Endekslerde Bulunan Şirketler(BIST 30, BIST 50 ve BIST 100 için)",
                            "subscription": None, "filter_value": None}
    
    endeksvolatilite_dict = {"category": None, "group": None,
                            "sub_category": None, "product_type": None,
                            "subscription": "[03.03.2024 - 03.01.2025] - Endeks Verileri Aboneliği (10 Ay) / EV", "filter_value": "ENDEKSVOLATILITE"}

class DSDownloadWebelements:
    
    """
    DataStore sitesinde veri indirme işlemleri için kullanılan webelement değişkenlerini içerir.
    """
    
    intercepted_value = False
    name_error_value = False
    link_error_value = False
    
    name_text = None
    link_text = None
    
    download_names = []
    download_links = []
    
    # Webelement arama stringleri.
    product_item_header_tuple = (_By.CLASS_NAME, "product-item-header")
    product_item_header_webelements = None
    
    product_item_header_collapsed_tuple = (_By.CSS_SELECTOR, ".product-item-header.collapsed")
    product_item_header_collapsed_webelements = None

    @staticmethod
    def get_name_webelement(i: int):
        return (_By.XPATH, f"/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[5]/ul/li[{i}]/div/div/div/div[2]/div[1]/div[1]/div[2]")

    @staticmethod
    def get_link_webelement(i: int):
        return (_By.XPATH, f"/html/body/div[1]/div[1]/div/section/div[1]/div[2]/div[5]/ul/li[{i}]/div/div/div/div[2]/div[2]/a")

# Fintables webelement listesi.
class FTDivStandards:

    """
    Fintables sitesinde dinamik XPath arama stringlerinde kullanılan div değişkenlerini içerir.
    """
    
    # Fintables sitesinde kullanılan değişkenler.
    div_standard = True
    div1 = 4
    div2 = 4
    div3 = 9
    div2_index = 3

class FTWebElementStandards:
    
    """
    Fintables sitesinde kullanılan dinamik XPath stringlerindeki global div standartlarını ve değişkenlerini belirleyen fonksiyonları içerir.
    """

    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FTWebElementStandards, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, ftdivstandards: FTDivStandards) -> None:
        if not hasattr(self, "_initialized"):
            self.ftdivstandards = ftdivstandards
            self._initialized = True
    
    # Webelement standardını belirler.
    def set_standard_value(self, is_standard: bool) -> None:

        """
        Webelement standardını belirler.
        """

        if not isinstance(is_standard, bool):
            raise TypeError("is_standard değeri bool olmalıdır.")

        self.ftdivstandards.div_standard = is_standard

        return None

    # Webelement div değerlerini belirler.
    def set_webelement_standard(self) -> None:

        """
        Webelement div değerlerini belirler. 
        
        !!!DIV2_INDEX DEĞERİ GÜNCELLENMİYOR!!!
        """

        if self.ftdivstandards.div_standard == True:
            self.ftdivstandards.div1 = 4
            self.ftdivstandards.div2 = 4
            self.ftdivstandards.div3 = 9
            self.ftdivstandards.div2_index = 3

        elif self.ftdivstandards.div_standard == False:
            self.ftdivstandards.div1 = 4
            self.ftdivstandards.div2 = 3
            self.ftdivstandards.div3 = 9
            self.ftdivstandards.div2_index = 2

        else:
            self.ftdivstandards.div1 = 4
            self.ftdivstandards.div2 = 4
            self.ftdivstandards.div3 = 9
            self.ftdivstandards.div2_index = 3

        return None
    
class FTDataTimeWebelements:
    
    """
    Fintables sitesindeki veri yayın zamanı webelementlerini ve metodlarını içerir.
    """
    
    time_webelement : _WebElement = None

    # Veri yayın zamanı web elementi.
    @staticmethod
    def get_time_webelement(div1: int):
        """ Veri yayın zamanı. Xpath. """
        return (_By.XPATH, f"/html/body/div[{div1}]/div/div/main/div/div/div[1]/div/div[2]/button/span")
    
    @staticmethod
    def get_time_element(div1: int):
        """ Veri yayın zamanı. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[1]/div/div[2]/button/span/text()")

class FTLogInWebelements:
    
    """
    Fintables sitesine giriş yapmak için kullanılan webelement değişkenlerini içerir.
    """
    
    # Webelement arama stringleri.
    login_email_tuple = (_By.NAME, "email")
    login_password_tuple = (_By.NAME, "password")
    login_button_tuple = (_By.XPATH, "/html/body/div[1]/div[1]/div/form/button")
    
    # Webelement değişkenleri.
    email_input : _WebElement = None
    password_input : _WebElement = None
    login_button : _WebElement = None

class FTLayoutButtons:

    """
    Fintables sitesindeki görünüm butonu isimlerini içerir.
    """

    layout_small = "Küçük" # Text
    layout_big = "Büyük" # Text

class FTCardTabs:

    """
    Fintables sitesinde hisse kartlarında kullanılan sekme isimlerini içerir.
    """

    tab_ozet = "Özet" # Text
    tab_derinlik = "Derinlik" # Text
    tab_takas = "Takas" # Text
    tab_aracikurum = "Aracı Kurum" # Text

class FTMainWindowWebelements(FTCardTabs, FTLayoutButtons):
    
    """
    Fintables sitesinde ana pencere için kullanılan webelement değişkenleri ve metotlarını içerir.
    """
    
    all_card_tabs : list[_WebElement] = None
    unopened_card_tabs : list[_WebElement] = None
    
    layout_menu_button : _WebElement = None
    
    layout_small_button : _WebElement = None
    layout_big_button : _WebElement = None
    
    add_button : _WebElement = None
    stock_input : _WebElement = None
    
    # Layout butonları.
    @staticmethod
    def get_layout_button(layout_name: str):
        """ Layout seçme butonları. Xpath. """
        return (_By.XPATH, f"//div[text()='{layout_name}']") # Xpath

    @staticmethod
    def get_layout_menu_button(div1: int, div2: int):
        """ Layout seçme menüsü butonu. Xpath. """
        return (_By.XPATH, f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[1]/button")
    
    # Hisse kartı ekleme butonu.
    @staticmethod
    def get_add_button(div1: int, div2: int):
        """ Hisse kartı ekleme butonu. Xpath. """
        return (_By.XPATH, f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[1]/div[1]/button") # Xpath
    
    @staticmethod
    def get_stock_input(div3: int):
        """ Hisse kartı ekleme inputu. Xpath. """
        return (_By.XPATH, f"/html/body/div[{div3}]/div/div/div[1]/input") # Xpath
    
    # Hisse kartı tab webelementleri.
    @staticmethod
    def get_tab_button(tab_name: str):
        """ Hisse kartı sekme butonları. Xpath. """
        return (_By.XPATH, f"//button[text()='{tab_name}']") # Xpath

class FTStockWebelements:

    """
    Hisse kartlarındaki web elementleri tutan listeler.
    """

    # Hisse kartları.
    @staticmethod
    def get_stock_cards():
        """ Hisse kartları. Class Name. """
        return (f"rounded-lg border border-stroke-02 relative group backdrop-blur-xl") # Class name
    
    # Hisse web elementleri.
    @staticmethod
    def get_stock_code_webelement(div1: int, div2: int, a: int):
        """ Hisse kodu. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[3]/div/div[{a}]/div[2]/div[1]/a/div[2]/div[1]/text()")

    @staticmethod
    def get_current_price_webelement(div1: int, div2: int, a: int):
        """ Hissenin güncel fiyatı. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[3]/div/div[{a}]/div[2]/div[1]/a/div[3]/div/span/text()")

    @staticmethod
    def get_lowest_price_webelement(div1: int, div2: int, a: int):
        """ Hissenin gördüğü günlük en düşük fiyatı. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[3]/div/div[{a}]/div[2]/div[1]/div/div[4]/div[2]/span/text()")

    @staticmethod
    def get_highest_price_webelement(div1: int, div2: int, a: int):
        """ Hissenin gördüğü günlük en yüksek fiyatı. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[3]/div/div[{a}]/div[2]/div[1]/div/div[3]/div[2]/span/text()")

    @staticmethod
    def get_total_traded_value_webelement(div1: int, div2: int, a: int):
        """ Hissenin toplam işlem hacmi. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[3]/div/div[{a}]/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[2]/span/text()")

    @staticmethod
    def get_total_traded_volume_webelement(div1: int, div2: int, a: int):
        """ Hissenin toplam işlem adedi. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div[3]/div/div[{a}]/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[1]/div[2]/span/text()")

class FTIndexWebelements:

    """
    Gösterge endeks web elementlerini tutan değişkenler.
    """

    xu030_code = np.str_("XU030")

    xu100_code = np.str_("XU100")

    # Endeks web elementleri.
    @staticmethod
    def get_xu030_value_webelement(div1: int, div2: int):
        """ XU030 endeksinin anlık değeri. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div/div/div[2]/div/div/div/div[2]/span[1]/span/text()")

    @staticmethod
    def get_xu100_value_webelement(div1: int, div2: int):
        """ XU100 endeksinin anlık değeri. Xpath. """
        return (f"/html/body/div[{div1}]/div/div/main/div/div/div[{div2}]/div/div/div[1]/div/div/div/div[2]/span[1]/span/text()")

class GlobalVariables:
    
    """
    Bu modülde tasarlanmış global değişkenler. Birden fazla modülle paylaşılan webelement değişkenleri bu sınıfta tanımlanır.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GlobalVariables, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
    
    ftdivstandards = FTDivStandards()
    ftwebelementstandards = FTWebElementStandards(ftdivstandards)

global_variables = GlobalVariables() # Global değişkenlere erişim.
