import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

from acquisition.financialdata.historical_data_formalization import DSFormalization
from acquisition.financialdata.historical_data_acquisition import DSAcquisition
from database.acquisition.historical_database import DSDatabase

from loggingmodule import LoggerObjects, info, debug

def VM_TV():

    """
    Tarihsel Veri Modülü fonksiyonu. Bu fonksiyon, BIST Veri kütüphanesine giriş yapar,
    BIST Veri kütüphanesinden tarihsel verileri indirir ve ilgili klasöre kaydeder.
    """

    TV_logger = LoggerObjects.VM_TV_logger # VM_TV: Veri Modülü - Tarihsel Veri
    TV_logger.info("Tarihsel Veri Modülü başlatılıyor.")
    DSAcquisition.VM_TV_VEE() # Veri Elde Etme modülü
    df_list = DSFormalization.VM_TV_VB() # Veri Biçimlendirme modülü
    DSDatabase.VM_TV_VT(df_list) # Veri Tabanı modülü
    TV_logger.info("Tarihsel Veri Modülü tamamlandı.")
    return None

VM_TV()