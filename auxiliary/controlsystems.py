from datetime import datetime as _datetime, time as _dtime
import time as _time
from typing import Callable as _Callable

import requests as _requests
from logging import Logger as _Logger
from loggingmodule import LoggerObjects as _LoggerObjects
from dataclass import Clocks as _Clocks, StockExchangeTime as _SET

"""
Uygulama genelinde kullanılan kontrol sınıfları, fonksiyonları ve decoratorleri içerir.
"""

class ObserverBase:
    
    """
    ObserverBase sınıfı, gözlemci tasarım desenine uygun olarak tasarlanmış bir sınıftır.
    """
    
    def __init__(self) -> None:
        pass
    
    # Gözlemciye bildirim yapar. Override edilmesi gereken bir metoddur.
    def update(self) -> None:
        pass

class SubjectBase:
    
    """
    SubjectBase sınıfı, gözlemci tasarım desenine uygun olarak tasarlanmış bir sınıftır.
    """
    
    def __init__(self) -> None:
        self._observers = []
    
    def attach(self, observer: ObserverBase) -> None:
        self._observers.append(observer)
    
    def detach(self, observer: ObserverBase) -> None:
        self._observers.remove(observer)
    
    def notify(self) -> None:
        for observer in self._observers:
            observer.update()

# Belirli bir zaman aralığında veri çekme işlemlerini gerçekleştirmek için gerekli zaman aralığını belirler.
def time_interval(logger: _Logger, start_time: _dtime, end_time: _dtime) -> _Callable | None:

    """
    Fonksiyonun çalışması için gerekli zaman aralığında çalışmasını sağlar.
    """

    def decorator(func: _Callable) -> _Callable | None:

        def wrapper(*args, **kwargs):

            now = _datetime.now()
            today_start = _datetime.combine(now.date(), start_time)
            today_end = _datetime.combine(now.date(), end_time)
            now = now.replace(microsecond=0)  # Mikrosaniye kısmını sıfırlar.

            if now < today_start:
                logger.info("Fonksiyon belirlenen çalışma zaman aralığına henüz gelmedi.")
                wait_seconds = (today_start - now).total_seconds()
                hours, remainder = divmod(wait_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                wait_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                logger.info(f"Fonksiyonun çalışmaya başlaması için beklenen süre: {wait_time}")
                _time.sleep(wait_seconds + 0.1)  # Garanti olması için fazladan 0.1 saniye bekleme süresi eklenir.
                return func(*args, **kwargs)

            elif now > today_end:
                logger.warning("Fonksiyon belirlenen çalışma zaman aralığını geçmiş.")
                return None

            else:
                logger.info(f"Fonksiyon başlatılıyor.")
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

class ConnControl(SubjectBase):
    
    """
    İnternet bağlantısını kontrol eden fonksiyon, decorator ve metodları içerir.
    """
    
    # İnternet bağlantısını kontrol eder.
    @time_interval(_LoggerObjects.CC_logger, _SET.bist_exchange_opening_time, _SET.bist_exchange_closing_time)
    def conn_control(self, start_time: _dtime, stop_time: _dtime, url: str = "https://www.google.com/") -> None:
        
        """
        Uygulamanın internet bağlantısını istenen websitesine istek göndererek kontrol eder.
        
        !!! BIST açılış ve kapanış saatleri arasında çalışır. !!!

        !!! OBSERVER DESENİ GELİŞTİRİLECEK !!!
        """
        
        now_time = _datetime.now().time()
        
        if now_time > stop_time:
            return None
        
        elif now_time < start_time:
            wait_seconds = (_datetime.combine(_datetime.now().date(), start_time) - _datetime.now()).total_seconds()
            _time.sleep(wait_seconds + 0.1)
            
        while start_time <= now_time <= stop_time:
            
            try:
                _time.sleep(2)
                response = _requests.get(url, timeout=3)
            
            except _requests.ConnectionError:
                self.notify()
            
            _time.sleep(1)
            now_time = _datetime.now().time()
            
        return None

class ConnControlDecorator(ObserverBase):
    
    """
    İnternet bağlantısının olup olmamasına göre fonksiyonları durdurur veya devam ettirir.
    
    !!!MANTIKSAL TASARIM HENÜZ TAMAMLANMADI!!!
    
    !!!CANLI VERİ ELDESİ FONKSİYONUNDA İHTİYAÇ YOK FAKAT EMİR İLETİMİ İÇİN GEREKLİ OLABİLİR!!!
    """
    
    def __init__(self) -> None:
        super().__init__()

    def update(self) -> None:
        return self.conn_control_decorator(_LoggerObjects.CC_logger)

    def conn_control_decorator(self, logger: _Logger) -> _Callable | None:
        
        """
        İnternet bağlantısının olup olmamasına göre fonksiyonları durdurur veya devam ettirir.
        
        Tekrarlı işlemlerin olduğu fonksiyonlara bu decorator eklenmeli.
        """
        
        def decorator(func: _Callable) -> _Callable | None:
        
            def wrapper(*args, **kwargs):
                
                # İnternet bağlantısının kesilmesi durumunda.
                if _Clocks.conn_lost_event.value:
                    logger.debug("FinTables sitesine bağlantı kesildi.")
                    logger.debug("İnternet bağlantısının geri gelmesi bekleniyor.")
                    
                    while _Clocks.conn_lost_event.value:
                        _time.sleep(3)
                        
                    if _datetime.now().time() > _SET.bist_exchange_closing_time:
                        logger.debug("Borsa kapanış zamanı geçtiği için veri yayın zamanı elde etme işlemi durduruldu.")
                        return None
            
            return wrapper
        
        return decorator
