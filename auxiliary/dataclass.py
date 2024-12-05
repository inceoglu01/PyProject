from datetime import datetime as _datetime, time

from multiprocessing import shared_memory as _shm, Value as _Value
from threading import Lock as _ThLock
import numpy as _np

from queue import Queue as _ThQueue
from multiprocessing import Queue as _MpQueue

"""
Veri sınıfları.
"""

class Clocks:

    """
    Uygulamada kullanılan saatleri içeren sınıf.
    """

    data_clock = _Value('b', True) # Data broadcast time clock
    
    osd_clock = _Value('b', False) # Opening Stock Data clock
    oid_clock = _Value('b', False) # Opening Index Data clock
    tsd_clock = _Value('b', False) # Trading Stock Data clock
    tid_clock = _Value('b', False) # Trading Index Data clock
    csd_clock = _Value('b', False) # Closing Stock Data clock
    cid_clock = _Value('b', False) # Closing Index Data clock
    
    osa_clock = _Value('b', False) # Opening Stock Analysis clock
    oia_clock = _Value('b', False) # Opening Index Analysis clock
    tsa_clock = _Value('b', False) # Trading Stock Analysis clock
    tia_clock = _Value('b', False) # Trading Index Analysis clock
    csa_clock = _Value('b', False) # Closing Stock Analysis clock
    cia_clock = _Value('b', False) # Closing Index Analysis clock
    
    conn_lost_event = _Value('b', False) # Internet connection lost event
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Clocks, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

class DatabaseInsertionTime:
    
    bist_opening_session_insertion_time: time = _datetime.strptime("09:59:00", '%H:%M:%S').time()
    bist_trading_session_insertion_time: time = _datetime.strptime("18:02:00", '%H:%M:%S').time()
    bist_closing_session_insertion_time: time = _datetime.strptime("18:15:00", '%H:%M:%S').time()
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseInsertionTime, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
    
class StockExchangeTime:

    """
    Borsa açılış, seans ve kapanış saatlerini içeren sınıf. Statik.
    """

    bist_exchange_opening_time: time = _datetime.strptime("09:45:00", '%H:%M:%S').time()
    bist_opening_session_start_time: time = _datetime.strptime("09:56:10", '%H:%M:%S').time()
    bist_trading_session_opening_time: time = _datetime.strptime("10:00:00", '%H:%M:%S').time()
    bist_trading_session_closing_time: time = _datetime.strptime("18:00:00", '%H:%M:%S').time()
    bist_closing_session__start_time: time = _datetime.strptime("18:08:00", '%H:%M:%S').time()
    bist_exchange_closing_time: time = _datetime.strptime("20:10:00", '%H:%M:%S').time()
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StockExchangeTime, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

class BISTIndexData:
    
    index_codes : list[_np.str_] = []
    index_values : list[_np.float64] = []
    index_total_traded_volumes : list[_np.int64] = []
    index_total_traded_values : list[_np.int64] = []
    index_sets : list[set[_np.str_]] = []
    all_index_stocks : set[_np.str_] = None
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BISTIndexData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
    
    @classmethod
    def assign_all_index_stocks(cls, all_index_stocks: set[_np.str_]) -> None:
        
        """
        Tüm endeks hisselerini atar.
        """
        
        cls.all_index_stocks = all_index_stocks
        
        return None
    
    @classmethod
    def append_index_codes(cls, index_code: _np.str_) -> None:
        
        """
        Endeks kodlarını listeye ekler.
        """
        
        cls.index_codes.append(index_code)
        
        return None
    
    @classmethod
    def append_index_values(cls, index_value: _np.float64) -> None:
        
        """
        Endeks değerlerini listeye ekler.
        """
        
        cls.index_values.append(index_value)
        
        return None
    
    @classmethod
    def append_index_total_traded_volumes(cls, index_total_traded_volume: _np.int64) -> None:
        
        """
        Endeks toplam işlem hacimlerini listeye ekler.
        """
        
        cls.index_total_traded_volumes.append(index_total_traded_volume)
        
        return None
    
    @classmethod
    def append_index_total_traded_values(cls, index_total_traded_value: _np.int64) -> None:
        
        """
        Endeks toplam işlem değerlerini listeye ekler.
        """
        
        cls.index_total_traded_values.append(index_total_traded_value)
        
        return None
    
    @classmethod
    def add_index_total_traded_volume(cls, index_value: int, index_total_traded_volume: _np.int64) -> None:
        
        """
        Endeks toplam işlem hacmini listedeki belirli değişkene ekler.
        """
        
        cls.index_total_traded_volumes[index_value] += index_total_traded_volume
        
        return None
    
    @classmethod
    def add_index_total_traded_value(cls, index_value: int, index_total_traded_value: _np.int64) -> None:
        
        """
        Endeks toplam işlem değerini listedeki belirli değişkene ekler.
        """
        
        cls.index_total_traded_values[index_value] += index_total_traded_value
        
        return None
    
    @classmethod
    def append_index_sets(cls, index_set: set[_np.str_]) -> None:
        
        """
        Endeks setlerini listeye ekler.
        """
        
        cls.index_sets.append(index_set)
        
        return None

class BISTData:
    
    """
    BIST verilerini tutan sınıf.
    """
    
    stock_data : list = []
    index_data : list = []
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BISTData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

class BISTLiveData:
    
    raw_htmls = _ThQueue() # Webscrapping işlemlerinde kullanılan process içi kuyruk.
    stock_rows = _MpQueue() # Hisse verilerini tutan process içi kuyruk.
    index_rows = _MpQueue() # Endeks verilerini tutan process içi kuyruk.
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BISTLiveData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

class BISTDataFrames:

    """
    BIST veri çerçeveleri sınıfı.
    """

    stock_df = None
    index_df = None
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BISTDataFrames, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

class TradingDataFrames:

    """
    İşlem verilerini tutan veri çerçeveleri.
    """

    tdf_stock_df = None
    tdf_index_df = None
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TradingDataFrames, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

class DSFileData:

    """
    Veri depolama sınıfı.
    """

    file_names : list = []
    file_paths : list = []
    table_names : list = []
    file_dates : list = []
    
    unzipped_file_names : list = []
    unzipped_file_paths : list = []
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DSFileData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
    
class DSDataFrames:

    """
    Veri çerçeveleri sınıfı.
    """

    data_frames : list = []
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DSDataFrames, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

class GlobalDataObjects:
    
    """
    Global değişkenlere ait örnekleri tutan sınıf.
    """
    
    clocks = Clocks()
    database_insertion_time = DatabaseInsertionTime()
    stock_exchange_time = StockExchangeTime()
    bist_index_data = BISTIndexData()
    bist_data = BISTData()
    bist_live_data = BISTLiveData()
    bist_data_frames = BISTDataFrames()
    trading_data_frames = TradingDataFrames()
    ds_file_data = DSFileData()
    ds_data_frames = DSDataFrames()
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GlobalDataObjects, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True

globaldataobjects = GlobalDataObjects()
    
if __name__ == "__main__":

    print(Clocks.data_clock.value)
    print(Clocks.osa_clock.value)
    