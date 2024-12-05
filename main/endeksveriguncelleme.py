import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

from submodules.formalization import DSFormalization
from submodules.acquisition import DSAcquisition
from submodules.database import DSDatabase

from loggingmodule import LoggerObjects, info, debug

def VM_EVG():
    
    """
    Endeks Verileri Güncelleme fonksiyonu. Bu fonksiyon, BIST Veri kütüphanesine giriş yapar,
    BIST Veri kütüphanesinden endeks verilerini indirir ve ilgili klasöre kaydeder.
    """

    # Endeks Verileri Güncelleme modülü için log nesnesi oluşturur.
    EVG_logger = LoggerObjects.VM_EVG_logger # VM_EVG: Veri Modülü - Endeks Verileri Güncelleme
    EVG_logger.info("Endeks Verileri Güncelleme modülü başlatıldı.")
    DSAcquisition.VM_EVG_VEE() # Veri Elde Etme modülü
    df_list = DSFormalization.VM_EVG_VB() # Veri Biçimlendirme modülü
    DSDatabase.VM_EVG_VT(df_list) # Veri Tabanı modülü
    EVG_logger.info("Endeks Verileri Güncelleme modülü tamamlandı.")
    return None

VM_EVG()
