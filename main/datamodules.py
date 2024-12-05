import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

from submodules.formalization import DSFormalization
from submodules.acquisition import DSAcquisition
from submodules.database import DSDatabase

from globals import LoggerNames

from loggingmodule import Loggers, info, debug

def VM_TV():

    """
    Tarihsel Veri Modülü fonksiyonu. Bu fonksiyon, BIST Veri kütüphanesine giriş yapar,
    BIST Veri kütüphanesinden tarihsel verileri indirir ve ilgili klasöre kaydeder.
    """

    TV_logger = Loggers(LoggerNames.TV).create_log(debug, info) # VM_TV: Veri Modülü - Tarihsel Veri
    TV_logger.info("Tarihsel Veri Modülü başlatılıyor.")
    DSAcquisition.VM_TV_VEE() # Veri Elde Etme modülü
    df_list = DSFormalization.VM_TV_VB() # Veri Biçimlendirme modülü
    DSDatabase.VM_TV_VT(df_list) # Veri Tabanı modülü
    TV_logger.info("Tarihsel Veri Modülü tamamlandı.")
    return None

def VM_EVG():
    
    """
    Endeks Verileri Güncelleme fonksiyonu. Bu fonksiyon, BIST Veri kütüphanesine giriş yapar,
    BIST Veri kütüphanesinden endeks verilerini indirir ve ilgili klasöre kaydeder.
    """

    # Endeks Verileri Güncelleme modülü için log nesnesi oluşturur.
    EVG_logger = Loggers(LoggerNames.EVG).create_log(debug, info) # VM_EVG: Veri Modülü - Endeks Verileri Güncelleme
    EVG_logger.info("Endeks Verileri Güncelleme modülü başlatıldı.")
    DSAcquisition.VM_EVG_VEE() # Veri Elde Etme modülü
    df_list = DSFormalization.VM_EVG_VB() # Veri Biçimlendirme modülü
    DSDatabase.VM_EVG_VT(df_list) # Veri Tabanı modülü
    EVG_logger.info("Endeks Verileri Güncelleme modülü tamamlandı.")
    return None
