import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Program dosyalarının bulunduğu ana dizin eklenir.

from logging import Handler as _Handler, StreamHandler as _StreamHandler, Formatter as _Formatter, getLogger as _getLogger, Logger as _Logger
from logging import DEBUG as _DEBUG, INFO as _INFO, WARNING as _WARNING, ERROR as _ERROR, CRITICAL as _CRITICAL
from datetime import datetime
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from auxiliary.globals import LoggerNames, conn_string, DatabaseNames, DatabaseTables

"""
Loglama modülü
"""

# Handler sınıfı
class SQLAlchemyHandler(_Handler):

    """
    SQLAlchemyHandler sınıfı, logları veritabanına kaydeder.
    """
    

    # Tanımlamalar
    def __init__(self):
        _Handler.__init__(self)
        try:
            self.engine = create_engine(conn_string(DatabaseNames.program_db))
            self.metadata = MetaData()
            self.Sessionmaker = sessionmaker(bind=self.engine)
            self.session = self.Sessionmaker()
            self.logs = Table(DatabaseTables.logs, self.metadata, autoload_with=self.engine)
            
        except Exception as e:
            print(f"SQLAlchemyHandler Error: {e}")
            raise e

    # Logları veritabanına kaydeden Handler sınıfı
    def emit(self, record):

        # Log kaydının oluşturulma zamanını al.
        creation_time = datetime.strftime(datetime.fromtimestamp(record.created), "%Y-%m-%d %H:%M:%S.%f")
        creation_time = creation_time[:-3]

        # Logları verigtabanına ekle.
        self.session.execute(self.logs.insert().values(DATETIME=creation_time, MODULE=record.name, LOG_LEVEL=record.levelname, MESSAGE=record.msg))
        self.session.commit()

# Yeni Logger sınıfı.
class Logger:
    
    """
    Custom Logger sınıfı.
    """

    def __init__(self, module_name: str, l_level: int = 0, h_level: int = 0):

        """
        Logger nesnesi oluşturur.
        """

        # Logger nesnesi oluşturur.
        self.logger = _getLogger(module_name)

        # Log seviyesini ayarlar.
        self.logger.setLevel(l_level)
        
        # Eğer logger'a zaten handler eklenmişse, onları kaldır !!!!! NEDEN KALDIRIYORUM !!!!!
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
            
        # Database Handler oluştur.
        db_handler = SQLAlchemyHandler()

        # Console Handler oluştur.
        console_handler = _StreamHandler()
        console_handler.setLevel(h_level)

        # Log formatını oluştur.
        formatter = _Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Console handler için formatı ayarla.
        console_handler.setFormatter(formatter)

        # Handlerları logger'a ekle.
        self.logger.addHandler(db_handler)
        self.logger.addHandler(console_handler)

    @property
    def get_logger(self) -> _Logger:

        """
        Logger nesnesini döndürür.
        """

        return self.logger

# Uygulamada kullanılan logger nesneleri.
class LoggerObjects:

    """
    Uygulamada kullanılan logger nesneleri.
    """
    
    # Hata loggerları.
    SB_logger = Logger(module_name = "SeleniumBase", l_level = _DEBUG, h_level = _DEBUG).get_logger # SB logger: Selenium Browser class loggerı.
    SAB_logger = Logger(module_name = "SeleniumAutomationBase", l_level = _DEBUG, h_level = _DEBUG).get_logger # SOB logger: Selenium Automation Base class loggerı.
    SWB_logger = Logger(module_name = "SeleniumWebscrappingBase", l_level = _DEBUG, h_level = _DEBUG).get_logger # SWB logger: Selenium Webscrapping Base class loggerı.
    TI_logger = Logger(module_name = "TimeIntervals", l_level = _DEBUG, h_level = _DEBUG).get_logger # TI logger: Time Intervals class loggerı.
    CC_logger = Logger(module_name = "ConnControl", l_level = _DEBUG, h_level = _DEBUG).get_logger # CC logger: Connection Control class loggerı.

    # Anlık Veri Elde Etme Modülü loggerları. !!! KODLAR GÖZDEN GEÇİRİLECEK !!!
    CDA_logger = Logger(module_name = "FT-CDA", l_level = _DEBUG, h_level = _DEBUG).get_logger # CDA logger: Current Data Acquisition class loggerı.
    FLI_logger = Logger(module_name = "FT-LogIn", l_level = _DEBUG, h_level = _DEBUG).get_logger # FTL logger: FinTables Login class loggerı.
    FMW_logger = Logger(module_name = "FT-MainWindow", l_level = _DEBUG, h_level = _DEBUG).get_logger # FTM logger: FinTables MainWindow class loggerı.
    FDT_logger = Logger(module_name = "FT-DataTimeACQ", l_level = _DEBUG, h_level = _DEBUG).get_logger # FDT logger: FinTables Data Time class loggerı.
    FLD_logger = Logger(module_name = "FT-LiveDataACQ", l_level = _DEBUG, h_level = _DEBUG).get_logger # FLD logger: FinTables Live Data class loggerı.
    HTP_logger = Logger(module_name = "FT-HTMLParser", l_level = _DEBUG, h_level = _DEBUG).get_logger # HTP logger: HTML Parser class loggerı.
    
    # Logger nesneleri.
    HDM_logger = Logger(module_name = "HDM", l_level = _DEBUG, h_level = _DEBUG).get_logger # FTE logger: FinTables Elde Etme class loggerı.
    LogIn_logger = Logger(module_name = "LogIn", l_level = _DEBUG, h_level = _DEBUG).get_logger # LogIn logger: Giriş yapma class loggerı.
    WEC_logger = Logger(module_name = "WEC", l_level = _DEBUG, h_level = _DEBUG).get_logger # WEC logger: WebElements Class class loggerı.
    CDM_logger = Logger(module_name = "CDM", l_level = _DEBUG, h_level = _INFO).get_logger # CDM logger: Current Data Module class loggerı.
    DSF_logger = Logger(module_name = "DSF", l_level = _DEBUG, h_level = _INFO).get_logger # DSF logger: DataStore Filtreleme class loggerı.
    DSI_logger = Logger(module_name = "DSI", l_level = _DEBUG, h_level = _INFO).get_logger # DSI logger: DataStore İndirme class loggerı.

    VM_TV_logger = Logger(module_name = LoggerNames.VM_TV, l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_TV_VEE_logger = Logger(module_name = LoggerNames.VM_TV_VEE, l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_TV_VT_logger = Logger(module_name = LoggerNames.VM_TV_VT, l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_TV_VB_logger = Logger(module_name = LoggerNames.VM_TV_VB, l_level = _DEBUG, h_level = _DEBUG).get_logger

    VM_EVG_logger = Logger(module_name = LoggerNames.VM_EVG , l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_EVG_VEE_logger = Logger(module_name = LoggerNames.VM_EVG_VEE, l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_EVG_VT_logger = Logger(module_name = LoggerNames.VM_EVG_VT, l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_EVG_VB_logger = Logger(module_name = LoggerNames.VM_EVG_VB, l_level = _DEBUG, h_level = _DEBUG).get_logger

    VM_AV_VEE_logger = Logger(module_name = LoggerNames.VM_AV_VEE, l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_AV_VT_logger = Logger(module_name = LoggerNames.VM_AV_VT, l_level = _DEBUG, h_level = _DEBUG).get_logger

    VM_AV_G_logger = Logger(module_name = LoggerNames.VM_AV_G, l_level = _DEBUG, h_level = _DEBUG).get_logger
    VM_TV_VEE_G_logger = Logger(module_name = LoggerNames.VM_TV_VEE_G, l_level = _DEBUG, h_level = _DEBUG).get_logger

    VM_TV_VEE_I_logger = Logger(module_name = LoggerNames.VM_TV_VEE_I, l_level = _DEBUG, h_level = _DEBUG).get_logger

    GSF_logger = Logger(module_name = LoggerNames.VM_TV_VB_GSF, l_level = _DEBUG, h_level = _DEBUG).get_logger
    GSE_logger = Logger(module_name = LoggerNames.VM_TV_VB_GSE, l_level = _DEBUG, h_level = _DEBUG).get_logger
    EEH_logger = Logger(module_name = LoggerNames.VM_TV_VB_EEH, l_level = _DEBUG, h_level = _DEBUG).get_logger

    CEH_logger = Logger(module_name = LoggerNames.VM_EVG_VB_CEH, l_level = _DEBUG, h_level = _DEBUG).get_logger
    EV_logger = Logger(module_name = LoggerNames.VM_EVG_VB_EV, l_level = _DEBUG, h_level = _DEBUG).get_logger
    
    DSFo_logger = Logger(module_name = LoggerNames.DSFo, l_level = _DEBUG, h_level = _DEBUG).get_logger
    
    # Database loggerları
    DBB_logger = Logger(module_name = LoggerNames.DBB, l_level = _DEBUG, h_level = _DEBUG).get_logger # DBB logger: Database Base class loggerı.
    DSD_logger = Logger(module_name = LoggerNames.DSD, l_level = _DEBUG, h_level = _DEBUG).get_logger # DSD logger: Data Store Database class loggerı.
    FTD_logger = Logger(module_name = LoggerNames.FTD, l_level = _DEBUG, h_level = _DEBUG).get_logger # FTD logger: FinTables Database class loggerı.

    Test13_logger = Logger(module_name = "Test13", l_level = _DEBUG, h_level = _INFO).get_logger
    Test14_logger = Logger(module_name = "Test14", l_level = _DEBUG, h_level = _INFO).get_logger
    Test15_logger = Logger(module_name = "Test15", l_level = _DEBUG, h_level = _INFO).get_logger
    
if __name__ == "__main__":
    
    LoggerObjects.Test13_logger.info("FTE logger _DEBUG")