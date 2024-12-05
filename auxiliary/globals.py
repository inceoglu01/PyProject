"""
Bu dosyanın amacı uygulamalarda kullanılan uzun liste, dict, tuple ve stringlerin bu dosyada tutularak ana kod dosyasının kolay
okunabilirliğini sağlamak ve karmaşıklık yaratılmasını önlemektir.
"""

from datetime import datetime as _datetime, time as _dt_time
from logging import Logger as _Logger
import time as _time

# DataFramelerdeki düzenleme işlemlerinde kullanılan silinecek sütunların listesi.
class Deletables:

    """
    DataFramelerdeki düzenleme işlemlerinde kullanılan silinecek sütunların listesini içerir.
    """

    fiyathacim = ["INSTRUMENT_NAME", "BIST_30_INDEX", "BIST_100_INDEX", "MARKET_SEGMENT", "MARKET_SUB_SEGMENT", "MARKET", "INSTRUMENT_GROUP", 
        "INSTRUMENT_TYPE", "INSTRUMENT_CLASS", "TRADING_METHOD", "MARKET_MAKER", "CORPORATE_ACTION", "REFERENCE_PRICE", 
        "LOWEST_SHORT_SALE_PRICE", "HIGHEST_SHORT_SALE_PRICE", "SHORT_SALE_VWAP", "TRADED_VALUE_OF_SHORT_SALE_TRADES", 
        "TRADED_VOLUME_OF_SHORT_SALE_TRADES", "NUMBER_OF_CONTRACTS_OF_SHORT_SALE_TRADES", "LOWEST_TRADE_REPORT_PRICE", 
        "HIGHEST_TRADE_REPORT_PRICE", "TRADE_REPORT_VWAP", "TRADE_REPORT_TRADED_VALUE", 
        "TRADE_REPORT_TRADED_VOLUME", "NUMBER_OF_TRADE_REPORTS"]

    endekshacim = ["INDEX_NAMES_IN_TURKISH", "INDEX_NAMES_IN_ENGLISH", "INDEX_TYPE", "DIVISOR"]

    cariendekshisse = []

    endeksvolatilite = ["INDEX_NAMES_IN_TURKISH", "INDEX_NAMES_IN_ENGLISH"]

    eskiendekshisse = ["STOCK_NAMES_IN_TURKISH"]

    eskiendekshisse_V2 = ["STOCK_NAMES_IN_TURKISH", "DELETABLE_COLUMN"]

# Dosya isimleri
class DSFileNames:
    
    """
    DataStore dosya isimlerini içerir.
    """

    ENDEKSVOLATILITE = "ENDEKSVOLATILITE"
    ESKIENDEKS = "exsrk"
    CARIENDEKS = "hisse_endeks_ds"
    ENDEKSHACIM = "PP_GUNSONUENDEKS"
    FIYATHACIM = "PP_GUNSONUFIYATHACIM"
    
    UNZIPPED_ENDEKSHACIM = "PP_GUNSONUENDEKS_M.csv"
    UNZIPPED_VOLATILITE_030 = "volatilite_XU030.csv"
    UNZIPPED_VOLATILITE_100 = "volatilite_XU100.csv"

    @classmethod
    def get_file_name_list(cls):
        return [value for name, value in cls.__dict__.items() if not name.startswith('__') and isinstance(value, str)]

# Dosya uzantıları
class FileExtensions:

    """
    Dosya uzantılarını içerir.
    """

    CSV = ".csv"
    XLS = ".xls"
    XLSX = ".xlsx"
    ZIP = ".zip"

# CSV/XLS dosyasını DataFrame biçimine dönüştürürken kullanılan başlık isimleri.
class ColumnNames:

    """
    CSV/XLS dosyasını DataFrame biçimine dönüştürürken kullanılan başlık isimlerini içerir.
    """

    fiyathacim = ["DATE", "STOCK_CODE", "INSTRUMENT_NAME", "MARKET_SUB_SEGMENT", "MARKET_SEGMENT", 
                                "MARKET", "INSTRUMENT_GROUP", "INSTRUMENT_TYPE", "INSTRUMENT_CLASS", "TRADING_METHOD",
                                "MARKET_MAKER", "BIST_100_INDEX", "BIST_30_INDEX", "GROSS_SETTLEMENT", "CORPORATE_ACTION", "SUSPENDED", "PREVIOUS_LAST_PRICE",
                                "OPENING_PRICE", "OPENING_SESSION_PRICE", "LOWEST_PRICE", "HIGHEST_PRICE", "CLOSING_PRICE", "CLOSING_SESSION_PRICE",
                                "CHANGE_TO_PREVIOUS_CLOSING_PRICE", "REMAINING_BID", "REMAINING_ASK", "VWAP", "TOTAL_TRADED_VALUE", "TOTAL_TRADED_VOLUME",
                                "TOTAL_NUMBER_OF_CONTRACTS", "REFERENCE_PRICE", "TRADED_VALUE_AT_OPENING_SESSION", "TRADED_VOLUME_AT_OPENING_SESSION",
                                "NUMBER_OF_CONTRACTS_AT_OPENING_SESSION", "TRADED_VALUE_AT_CLOSING_SESSION", "TRADED_VOLUME_AT_CLOSING_SESSION",
                                "NUMBER_OF_CONTRACTS_AT_CLOSING_SESSION", "TRADED_VALUE_OF_TRADES_AT_CLOSING_PRICE",
                                "TRADED_VOLUME_OF_TRADES_AT_CLOSING_PRICE", "NUMBER_OF_CONTRACTS_OF_TRADES_AT_CLOSING_PRICE", "LOWEST_SHORT_SALE_PRICE",
                                "HIGHEST_SHORT_SALE_PRICE", "SHORT_SALE_VWAP", "TRADED_VALUE_OF_SHORT_SALE_TRADES", "TRADED_VOLUME_OF_SHORT_SALE_TRADES", 
                                "NUMBER_OF_CONTRACTS_OF_SHORT_SALE_TRADES", "LOWEST_TRADE_REPORT_PRICE", "HIGHEST_TRADE_REPORT_PRICE", "TRADE_REPORT_VWAP", 
                                "TRADE_REPORT_TRADED_VALUE", "TRADE_REPORT_TRADED_VOLUME", "NUMBER_OF_TRADE_REPORTS"]

    endekshacim = ["DATE", "INDEX_CODE", "INDEX_NAMES_IN_TURKISH", "INDEX_NAMES_IN_ENGLISH", "INDEX_TYPE", "DIVISOR", 
                                "CLOSING_VALUE", "LOWEST_VALUE", "HIGHEST_VALUE", "TRADED_VALUE", "TRADED_VOLUME"]

    cariendekshisse = ["STOCK_CODE", "INDEX_CODE", "DATE"]

    endeksvolatilite = ["DATE", "INDEX_CODE", "INDEX_NAMES_IN_TURKISH", "INDEX_NAMES_IN_ENGLISH", "NUMBER_OF_DAYS", "VALUE"]

    eskiendekshisse = ["STOCK_CODE", "STOCK_NAMES_IN_TURKISH", "FIRST_QUARTER", "SECOND_QUARTER", "THIRD_QUARTER", "FOURTH_QUARTER"]

    eskiendekshisse_V2 = ["STOCK_CODE", "STOCK_NAMES_IN_TURKISH", "FIRST_QUARTER", "SECOND_QUARTER", "DELETABLE_COLUMN", "THIRD_QUARTER", "FOURTH_QUARTER"]

    fintables = ["TRADE DATE TIME", "STOCK CODE", "MIN PRICE", "OPENING PRICE", "LOWEST PRICE", "STOCK PRICE", "CHANGE RATE %", 
                       "TRADED VALUE", "HIGHEST PRICE", "CLOSING PRICE", "MAX PRICE", "BIST INDEX", "BIST INDEX VALUE", "INDEX CHANGE RATE %"]

# CSV/XLS dosyasını DataFrame biçimine dönüştürürken kullanılan tip-sütun dönüşümleri.
class Dtypes:

    """
    DataFrame dönüşümlerinde kullanılan tip-sütun dönüşümlerini içerir.
    """

    fiyathacim = {'DATE': 'str' ,'STOCK_CODE': 'str', 'BIST_100_INDEX': 'Int64',
                'BIST_30_INDEX': 'Int64', 'GROSS_SETTLEMENT': 'float', 'SUSPENDED': 'Int64', 'PREVIOUS_LAST_PRICE': 'float',
                'OPENING_PRICE': 'float', 'OPENING_SESSION_PRICE': 'float', 'LOWEST_PRICE': 'float',
                'HIGHEST_PRICE': 'float', 'CLOSING_PRICE': 'float', 'CLOSING_SESSION_PRICE': 'float',
                'CHANGE_TO_PREVIOUS_CLOSING_PRICE': 'float', 'REMAINING_BID': 'float', 'REMAINING_ASK': 'float',
                'VWAP': 'float', 'TOTAL_TRADED_VALUE': 'float', 'TOTAL_TRADED_VOLUME': 'Int64',
                'TOTAL_NUMBER_OF_CONTRACTS': 'Int64', 'TRADED_VALUE_AT_OPENING_SESSION': 'float',
                'TRADED_VOLUME_AT_OPENING_SESSION': 'Int64',
                'NUMBER_OF_CONTRACTS_AT_OPENING_SESSION': 'Int64',
                'TRADED_VALUE_AT_CLOSING_SESSION': 'float', 'TRADED_VOLUME_AT_CLOSING_SESSION': 'Int64',
                'NUMBER_OF_CONTRACTS_AT_CLOSING_SESSION': 'Int64',
                'TRADED_VALUE_OF_TRADES_AT_CLOSING_PRICE': 'float',
                'TRADED_VOLUME_OF_TRADES_AT_CLOSING_PRICE': 'Int64',
                'NUMBER_OF_CONTRACTS_OF_TRADES_AT_CLOSING_PRICE': 'Int64'}

    endekshacim = {"DATE": "str", "INDEX_CODE": "str", "INDEX_NAMES_IN_TURKISH": "str",
                    "INDEX_NAMES_IN_ENGLISH": "str", "INDEX_TYPE": "str",
                    "DIVISOR": "float", "CLOSING_VALUE": "float", "LOWEST_VALUE": "float",
                    "HIGHEST_VALUE": "float", "TRADED_VALUE": "float", "TRADED_VOLUME": "Int64"}

    cariendekshisse = {"STOCK_CODE": "str", "INDEX_CODE": "str", "DATE": "str"}

    eskiendekshisse = {"YEAR": "str", "STOCK_CODE": "str", "STOCK_NAMES_IN_TURKISH": "str", "FIRST_QUARTER": "str",
                        "SECOND_QUARTER": "str", "THIRD_QUARTER": "str", "FOURTH_QUARTER": "str"}

    eskiendekshisse_V2 = {"YEAR": "str", "STOCK_CODE": "str", "STOCK_NAMES_IN_TURKISH": "str", "FIRST_QUARTER": "str",
                        "SECOND_QUARTER": "str", "DELETABLE_COLUMN": "str", "THIRD_QUARTER": "str", "FOURTH_QUARTER": "str"}

    endeksvolatilite = {"DATE": "str", "INDEX_CODE": "str", "INDEX_NAMES_IN_TURKISH": "str", "INDEX_NAMES_IN_ENGLISH": "str",
                        "NUMBER_OF_DAYS": "Int64", "VALUE": "float"}

    anlikfiyat = {'TRADE DATE TIME': 'str', 'STOCK CODE': 'str', 'MIN PRICE': 'float', 
                'OPENING PRICE': 'float', 'LOWEST PRICE': 'float', 'STOCK PRICE': 'float', 'CHANGE RATE %': 'float',
                'TRADED VALUE': 'float', 'HIGHEST PRICE': 'float', 'CLOSING PRICE': 'float', 'MAX PRICE': 'float',
                'BIST INDEX': 'str', 'BIST INDEX VALUE': 'float', 'INDEX CHANGE RATE %': 'float'}

# Uygulamada kullanılan dosya yolları.
class Paths:

    """
    Uygulamada kullanılan dosya yollarını içerir.
    """

    prefs_indirme = {"download.default_directory" : r"C:\Yatırım\Veri Kaynakları\BIST\Pay Piyasası\Tarihi Veriler\Indirmeler"}

    indirme_dir = r"C:\Yatırım\Veri Kaynakları\BIST\Pay Piyasası\Tarihi Veriler\Indirmeler"

    zip_path = r"C:\Yatırım\Veri Kaynakları\BIST\Pay Piyasası\Tarihi Veriler\GUNSONUENDEKSHACIM\ZIP"
    unzip_path = r"C:\Yatırım\Veri Kaynakları\BIST\Pay Piyasası\Tarihi Veriler\GUNSONUENDEKSHACIM\CSV"

# Kullanıcı ve giriş bilgileri.
class LoginInfo:

    """
    BIST DataStore ve Fintables giriş bilgilerini içerir.
    """

    email = ""
    ds_password = ""
    ft_password = ""

# Web sitesi adresleri.
class WebSites:

    """
    Web sitesi adreslerini içerir.
    """

    fintables = "https://fintables.com/auth/login"
    datastore = "https://datastore.borsaistanbul.com/library"
    matriks = "https://www.matriksdata.com/"

# Logger isimleri.
class LoggerNames:

    """
    Logger isimlerini içerir.
    """

    VM_TV = "VM-TV" # VM_TV: Veri Modülü - Tarihsel Veri
    VM_TV_VEE = "VM-TV-VEE" # VM-TV-VEE: Veri Modülü - Tarihsel Veri - Veri Elde Etme
    VM_TV_VEE_G = "VM-TV-VEE-G" # VM-TV-VEE-G: Veri Modülü - Tarihsel Veri - Veri Elde Etme - Giriş
    VM_TV_VEE_I = "VM-TV-VEE-I" # VM-TV-VEE-I: Veri Modülü - Tarihsel Veri - Veri Elde Etme - İndirme
    VM_TV_VT = "VM-TV-VT" # VM-TV-VT: Veri Modülü - Tarihsel Veri - Veri Tabanı
    VM_TV_VB = "VM-TV-VB" # VM-TV-VB: Veri Modülü - Tarihsel Veri - Veri Biçimlendirme
    VM_TV_VB_GSF = "VM-TV-VB-GSF" # VM-TV-VB-GSF: Veri Modülü - Tarihsel Veri - Veri Biçimlendirme - Gün Sonu Fiyat
    VM_TV_VB_GSE = "VM-TV-VB-GSE" # VM-TV-VB-GSH: Veri Modülü - Tarihsel Veri - Veri Biçimlendirme - Gün Sonu Endeks
    VM_TV_VB_EEH = "VM-TV-VB-EEH" # VM-TV-VB-EEH: Veri Modülü - Tarihsel Veri - Veri Biçimlendirme - Eski Endeks Hisse

    VM_EVG = "VM-EVG" # VM_EVG: Veri Modülü - Endeks Verileri Güncelleme
    VM_EVG_VEE = "VM-EVG-VEE" # VM-EVG-VEE: Veri Modülü - Endeks Verileri Güncelleme - Veri Elde Etme
    VM_EVG_VB = "VM-EVG-VB" # VM-EVG-VB: Veri Modülü - Endeks Verileri Güncelleme - Veri Biçimlendirme
    VM_EVG_VT = "VM-EVG-VT" # VM-EVG-VT: Veri Modülü - Endeks Verileri Güncelleme - Veri Tabanı
    VM_EVG_VB_CEH = "VM-EVG-VB-CEH" # VM-EVG-VB-CEH: Veri Modülü - Endeks Verileri Güncelleme - Veri Biçimlendirme - Cari Endeks Hisse
    VM_EVG_VB_EV = "VM-EVG-VB-EV" # VM-EVG-VB-EV: Veri Modülü - Endeks Verileri Güncelleme - Veri Biçimlendirme - Endeks Volatilite

    VM_AV_VEE = "VM-AV-VEE" # VM-AV-VEE: Veri Modülü - Anlık Veri - Veri Elde Etme
    VM_AV_VT = "VM-AV-VT" # VM-AV-VT: Veri Modülü - Anlık Veri - Veri Tabanı
    VM_AV_G = "VM-AV-G" # VM-AV-G: Veri Modülü - Anlık Veri - Giriş
        
    DSFo = "DSFo" # DSFo: DataStore Biçimlendirme
    
    # Database loggerları
    DBB = "DBB" # DBB: Database Base
    DSD = "DSD" # DSD: Data Store Database
    FTD = "FTD" # FTD: FinTables Database
  
# SQL Server bağlantısı için kullanılan connection string.
def conn_string(db_name: str = "master"):

    """
    SQL Server bağlantısı için kullanılan connection stringi döndürür.
    """
    if db_name in DatabaseNames.get_db_list():
        return f"mssql+pyodbc://@./{db_name}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes&Trusted_Connection=yes"
    else:
        return None

# Veritabanı değişkenleri
class DatabaseNames:
    
    """
    SQL Server bağlantısı için kullanılan DB isimlerini içerir.
    """

    # Finansal Veri Veritabanları
    bist_current_data_db = "BIST_CURRENT_DATA" # Anlık Veriler DB. Borsaya dahil olan şirketlerin anlık borsa verileri: Fiyat, hacim, endeks değerleri, endeks hacimleri, emir-fiyat kademe verileri vb.
    bist_historical_data_db = "BIST_HISTORICAL_DATA" # Tarihsel Veriler DB. Borsaya dahil olan şirketlerin finansal verileri, tarihsel oran ve değerleri: Tarihsel fiyatlar, bilanço verileri, oranlar, değerler vb.
    economic_data_db = "ECONOMIC_DATA" # Ekonomik Veriler DB. İktisadi veriler, iktisadi oranlar, iktisadi değerler, iktisadi endeksler vb. Makroekonomik veriler, mikroekonomik veriler, sektörel veriler vb.

    # Faaliyet Veritabanları
    financial_data_db = "FINANCIAL_DATA" # Gerçekleştirilen faaliyete yönelik finansal veriler DB. Portföy verileri, komisyon verileri, işlem verileri.
    activity_data_db = "ACTIVITY_DATA" # Borsaya iletilen emirler ve gerçekleşen işlemler DB. Emir verileri, işlem verileri.

    # Analiz Verileri Veritabanları
    current_analysis_db = "DYNAMIC_ANALYSIS" # Anlık analiz DB. Güncel analiz verileri, güncel oranlar, güncel değerler vb.
    historical_analysis_db = "STATIC_ANALYSIS" # Tarihsel analiz DB. Tarihsel analiz verileri, tarihsel oranlar, tarihsel değerler vb.
    financial_analysis_db = "FINANCIAL_ANALYSIS" # Finansal analiz DB. Faaliyete ilişkin analiz verileri, finansal oranlar, finansal değerler, bilançolar vb.
    program_analysis_db = "PROGRAM_ANALYSIS" # Program analiz DB. Log analiz verileri, performans analizi verileri, hata analizi verileri vb.
    ordering_analysis_db = "ORDERING_ANALYSIS" # Emir analiz DB. Emir iletim analizi verileri, gerçekleşen işlem analiz verileri, portföy analiz verileri (?) vb.

    # Program Verileri Veritabanları
    program_db = "PROGRAM_DATA" # Program verileri DB. Program ayarları, program verileri, program değişkenleri, program sabitleri, log vb.

    # Deneme Veritabanları
    deneme = "DENEME" # Deneme için kullanılan DB.

    @classmethod
    def get_db_list(cls) -> list[str]:
        return [value for name, value in vars(cls).items() if not name.startswith('__') and not callable(value) and not isinstance(value, classmethod)]

class DatabaseTables:

    """
    SQL Server bağlantısı için kullanılan tablo isimlerini içerir.
    """

    # Tarihsel Veriler Veritabanı Tabloları
    datastore_h_stock = "DS_H_STOCK_DATA" # BIST Fiyat ve Hacim Tarihsel Veriler Tablosu.
    datastore_h_index = "DS_H_INDEX_DATA" # BIST Endeks Hacim Tarihsel Veriler Tablosu.
    datastore_c_stock_index = "DS_C_STOCK_INDEX" # BIST Cari Endeks Hisse Tablosu.
    datastore_h_volatility = "DS_H_INDEX_VOLATILITY" # BIST Endeks Volatilite Tablosu.
    datastore_h_stock_index = "DS_H_STOCK_INDEX" # BIST Eski Endeks Hisse Tablosu.

    matriks_tarihsel_fiyat = "M_H_STOCK_DATA" # Matrisk Tarihsel Fiyat Hacim Tablosu.

    # Anlık Veriler Veritabanı Tabloları
    fintables_c_stock = "FT_C_STOCK_DATA" # Fintables Fiyat ve Hacim Anlık Veriler Tablosu.
    fintables_c_stock_opening = "FT_C_STOCK_DATA_OPENING" # Fintables Açılış Anlık Veriler Tablosu.
    fintables_c_stock_closing = "FT_C_STOCK_DATA_CLOSING" # Fintables Kapanış Anlık Veriler Tablosu.
    fintables_c_index = "FT_C_INDEX_DATA" # Fintables Endeks Hacim Anlık Veriler Tablosu.
    fintables_c_index_opening = "FT_C_INDEX_DATA_OPENING" # Fintables Endeks Açılış Anlık Veriler Tablosu.
    fintables_c_index_closing = "FT_C_INDEX_DATA_CLOSING" # Fintables Endeks Kapanış Anlık Veriler Tablosu.

    fintables_c_swap = "FT_H_SWAP" # Fintables Takas Günlük Veriler Tablosu. Daha tasarlanmadı!!!

    fintables_h_stock = "FT_H_STOCK_DATA" # Fintables Tarihsel Veriler Tablosu.
    fintables_h_stock_opening = "FT_H_STOCK_DATA_OPENING" # Fintables Açılış Tarihsel Veriler Tablosu.
    fintables_h_stock_closing = "FT_H_STOCK_DATA_CLOSING" # Fintables Kapanış Tarihsel Veriler Tablosu.
    fintables_h_index = "FT_H_INDEX_DATA" # Fintables Tarihsel Endeks Veriler Tablosu.
    fintables_h_index_opening = "FT_H_INDEX_DATA_OPENING" # Fintables Açılış Tarihsel Endeks Veriler Tablosu.
    fintables_h_index_closing = "FT_H_INDEX_DATA_CLOSING" # Fintables Kapanış Tarihsel Endeks Veriler Tablosu.

    fintables_h_swap = "FT_H_SWAP" # Fintables Takas Tarihsel Veriler Tablosu. Daha tasarlanmadı!!!

    # Faaliyet Veri Tabloları
    portfolio_c_data = "PORTFOLIO_CURRENT_DATA" # Portföy Anlık Verileri Tablosu.
    orders_c_data = "ORDERS_CURRENT_DATA" # Günlük İşlemler Anlık Verileri Tablosu.

    portfolio_h_data = "H_PORTFOLIO_DATA" # Portföy Tarihsel Verileri Tablosu.
    orders_h_data = "H_ORDERS" # Günlük İşlemler Tarihsel Verileri Tablosu.

    # Program Verileri Veritabanı Tabloları
    logs = "LOGS" # Log Tablosu.
    performance_data = "PERFORMANCE_DATA" # Program Performans Verileri Tablosu.

    # Analiz Verileri Veritabanı Tabloları
    current_data_analysis = "CURRENT_H_ANALYSIS" # Tarihsel Analiz Tablosu.
    historical_data_analysis = "HISTORICAL_D_ANALYSIS" # Günlük Analiz Tablosu.

    @classmethod
    def get_table_list(cls) -> list[str]:
        return [value for name, value in vars(cls).items() if not name.startswith('__') and not callable(value) and not isinstance(value, classmethod)]

# Pandas DataFrame dönüşümlerinde kullanılan sütun isimleri.
class OpeningSessionColumns:

    """
    Pandas DataFrame dönüşümlerinde kullanılan sütun isimlerini içerir.
    """

    stock_date_column = "DATE"
    stock_code_column = "STOCK_CODE"
    stock_min_price_column = "MIN_PRICE"
    stock_opening_price_column = "OPENING_PRICE"
    stock_change_rate_column = "CHANGE_RATE"
    stock_max_price_column = "MAX_PRICE"

    index_date_column = "DATE"
    index_code_column = "INDEX_CODE"
    index_opening_value_column = "OPENING_VALUE"
    index_change_rate_column = "CHANGE_RATE"

class TradingSessionColumns:

    """
    Pandas DataFrame dönüşümlerinde kullanılan sütun isimlerini içerir.
    """

    stock_datetime_column = "DATETIME"
    stock_code_column = "STOCK_CODE"
    stock_lowest_price_column = "LOWEST_PRICE"
    stock_current_price_column = "STOCK_PRICE"
    stock_change_rate_column = "CHANGE_RATE"
    stock_traded_volume_column = "TOTAL_TRADED_VOLUME"
    stock_traded_value_column = "TOTAL_TRADED_VALUE"
    stock_highest_price_column = "HIGHEST_PRICE"

    index_datetime_column = "DATETIME"
    index_code_column = "INDEX_CODE"
    index_current_value_column = "VALUE"
    index_change_rate_column = "CHANGE_RATE"

class ClosingSessionColumns:

    """
    Pandas DataFrame dönüşümlerinde kullanılan sütun isimlerini içerir.
    """

    stock_date_column = "DATE"
    stock_code_column = "STOCK_CODE"
    stock_closing_price_column = "CLOSING_PRICE"
    stock_change_rate_column = "CHANGE_RATE"
    stock_traded_volume_column = "TOTAL_TRADED_VOLUME"
    stock_traded_value_column = "TOTAL_TRADED_VALUE"

    index_date_column = "DATE"
    index_code_column = "INDEX_CODE"
    index_closing_value_column = "CLOSING_VALUE"
    index_change_rate_column = "CHANGE_RATE"
