import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python")

from loggingmodule import LoggerObjects, debug, info, warning, error, critical
from errorhandling import SQLAlchemyErrorHandling
from datetime import datetime as _datetime
import logging
import time as _time
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor

from sqlalchemy import MetaData, and_
from database.database import CurrentDatabase, DatabaseTables, DatabaseNames, create_db_engine
from sqlalchemy.orm import Session

from auxiliary.dataclass import TradingStockData, TradingIndexData, OpeningStockData, OpeningIndexData, ClosingStockData, ClosingIndexData, StockExchangeTime, DatabaseInsertionTime
from auxiliary.controlsystems import time_interval

"""
Anlık verilerin veritabanına yazılması, istenildiği zaman verilerin çekilmesi
ve veritabanındaki verilerin güncellenmesi işlemlerini gerçekleştiren modül.
"""

class FTCurrentDatabase(CurrentDatabase):
    
    """
    FTCurrentDatabase sınıfı, finansal verilerin veritabanı sorgu ve veri ekleme işlemlerini gerçekleştirmek
    için gerekli metotları içerir.
    
    Fintables sitesini kullanan veri elde etme işlemi için baz sınıftır.
    """
    
    CD_engine = create_db_engine(DatabaseNames.bist_current_data_db)
    
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__(self.CD_engine, MetaData(), logger)

class FTQuery(FTCurrentDatabase):

    """
    FTQuery sınıfı, veritabanından veri çekme işlemlerini gerçekleştirmek için gerekli metotları içerir.
    """

    def __init__(self) -> None:
        super().__init__(LoggerObjects.FTD_logger)

    # Belirtilen tarihe ilişkin endeks kodlarını elde eder.
    def get_index_codes(self, date: str = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d")) -> list:
        
        """
        DS_C_STOCK_INDEX tablosundaki belirtilen güne ait endeks kodlarını elde eder.
        
        date: str -> Tarih. Belirtilen tarihe ait endeks kodlarını elde etmek için kullanılır.
        """
        
        @SQLAlchemyErrorHandling.unexpected_error(logger= self.logger, gmessage= "Endeks kodları elde edilemedi.", exit= True)
        def get_index_codes(date: str = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d")) -> list:
            
            self.logger.debug("Endeks kodlarını elde etme fonksiyonu çalıştırılıyor.")

            session = self.Session()

            table = self.get_table_object(DatabaseTables.datastore_c_stock_index) # Tablo ön tanımlı fakat dinamik hale getirilebilir.
            
            index_code_rows = session.query(table.c.INDEX_CODE).filter(table.c.DATE == date).distinct().all()
            index_code_list = [row[0] for row in index_code_rows]
            index_code_list.sort()
            self.logger.debug("Endeks kodları alındı.")
            
            session.close()
            
            self.logger.debug("Endeks kodlarını elde etme fonksiyonu tamamlandı.")
            
            return index_code_list
        
        return get_index_codes(date)
            
    # Belirtilen tarihteki hisse kodlarını istenen endekse bağlı olarak elde etme
    def get_stock_codes(self, index_type: str = XU030, date: str = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d")) -> list:
        
        """
        DS_C_STOCK_INDEX tablosundaki belirtilen endekse ve güne ait hisse kodlarını elde eder.
        
        :param index_type: str -> Endeks ismi. Belirtilen endekse dahil olan hisselerin kodlarını elde etmek için kullanılır.
        :param date: str -> Tarih. Belirtilen tarihe ait hisse isimlerini elde etmek için kullanılır.
        """

        @SQLAlchemyErrorHandling.unexpected_error(logger= self.logger, gmessage= "Hisse kodları elde edilemedi.", exit= True)
        def get_stock_codes(index_type: str = XU030, date = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d")) -> list:

            self.logger.debug("Hisse kodlarını elde etme fonksiyonu çalıştırılıyor.")

            session = self.Session()

            table = self.get_table_object(DatabaseTables.datastore_c_stock_index) # Tablo ön tanımlı fakat dinamik hale getirilebilir.

            stock_rows = session.query(table.c.STOCK_CODE).filter(and_(table.c.INDEX_CODE == index_type, table.c.DATE == date)).all()
            stock_list = [row[0] for row in stock_rows]
            stock_list.sort()
            self.logger.debug("Hisse kodları alındı.")

            session.close()

            self.logger.debug("Hisse kodlarını elde etme fonksiyonu tamamlandı.")

            return stock_list

        return get_stock_codes(index_type, date)

class FTInsert(FTCurrentDatabase, TradingStockData, TradingIndexData, OpeningStockData, OpeningIndexData, ClosingStockData, ClosingIndexData):
    
    """
    FTInsert sınıfı, veritabanına veri ekleme işlemlerini gerçekleştirmek için gerekli metotları içerir.
    """

    def __init__(self) -> None:
        super().__init__(LoggerObjects.FTD_logger)

    # Verileri veritabanına ekler.
    @FTCurrentDatabase.get_session(FTCurrentDatabase)
    def __data_to_sql(self, dicts: list[dict], table_name: str, index: bool = False, stock: bool = False) -> None:

        """
        Veritabanına dict türündeki verileri ekler. Dict keyleri column isimlerine karşılık gelmelidir.
        
        Batch operasyonları için uygundur.
        """

        if index and stock:
            self.logger.debug("Endeks ve hisse verisi aynı anda aktarılamaz.")
            return None
        
        elif not index and not stock:
            self.logger.debug("Endeks veya hisse verisi belirtilmedi.")
            return None
                
        if dicts == [] or dicts == None:
            self.logger.warning(f"{table_name} tablosuna eklenecek veri bulunamadı.")
            return None

        table = self.get_table_object(table_name)

        self._session.execute(table.insert(), dicts)
        self.logger.debug(f"{table_name} tablosuna veri eklendi.")

        return None

    # Açılış verilerini veritabanına ekler.
    def __opening_data_to_sql(self, dicts: list[dict], session: Session, index: bool = False, stock: bool = False) -> None:

        """
        FINANCIAL_DATA veritabanındaki FT_H_MAXMIN adlı tabloya veri ekler.
        """

        if index and not stock:
            table_name = DatabaseTables.fintables_c_index_opening

        elif stock and not index:
            table_name = DatabaseTables.fintables_c_stock_opening
            
        self.__data_to_sql(dicts, session, table_name, index, stock)
        
        return None
    
    # Anlık verileri veritabanına ekler.
    def __current_data_to_sql(self, dicts: list[dict], session: Session, index: bool = False, stock: bool = False) -> None:

        """
        FINANCIAL_DATA veritabanındaki FT_CURRENT_DATA adlı tabloya veri ekler.
        """

        if index and not stock:
            table_name = DatabaseTables.fintables_c_index

        elif stock and not index:
            table_name = DatabaseTables.fintables_c_stock

        self.__data_to_sql(dicts, session, table_name, index, stock)

        return None
    
    # Kapanış verilerini veritabanına ekler.
    def __closing_data_to_sql(self, dicts: list[dict], session: Session, index: bool = False, stock: bool = False) -> None:

        """
        FINANCIAL_DATA veritabanındaki FT_H_MAXMIN adlı tabloya veri ekler.
        """

        if index and not stock:
            table_name = DatabaseTables.fintables_c_index_closing

        elif stock and not index:
            table_name = DatabaseTables.fintables_c_stock_closing

        self.__data_to_sql(dicts, session, table_name, index, stock)

        return None
    
    # Anlık verileri veritabanına ekler.
    @time_interval(LoggerObjects.FTD_logger, StockExchangeTime.bist_opening_session_start_time, StockExchangeTime.bist_trading_session_opening_time)
    def insert_opening_data(self, index: bool, stock: bool) -> None:

        """
        Açılış verilerini dictlere dönüştürüp veritabanına ekler.
        """
        
        #############################################################################
        # İnternet kesilmesine karşı koruma sağlıyor fakat elektrik kesilmesine karşı
        # koruma sağlamıyor. Bu durumda veri kaybı yaşanabilir.
        #############################################################################

        self.logger.debug("Endeks açılış değerleri veritabanına kaydediliyor.")

        # Veri elde etme işlemi tamamlanana dek.
        while not Clocks.oid_clock.value and not Clocks.osd_clock.value:
            _time.sleep(1)
            
            # İnternet bağlantısının kesilmesi durumunda.
            if Clocks.conn_lost_event.value:
                self.logger.debug("FinTables sitesine bağlantı kesildi.")
                self.logger.debug("İnternet bağlantısının geri gelmesi bekleniyor.")
                
                while Clocks.conn_lost_event.value:
                    _time.sleep(3)
                    
                if _datetime.now().time() > StockExchangeTime.bist_trading_session_opening_time:
                    self.logger.debug("Borsa açılış seansı zamanı geçtiği için halihazırda elde edilmiş açılış seansı verileri veritabanına aktarılıyor.")
                    break
                
        # Ön tanımlı veri aktarma işlemi.
        if index and not stock:
            
            data_dicts = [
                {'DATE': date, 'INDEX_CODE': index_code, 'OPENING_VALUE': opening_value} 
                for date, index_code, opening_value in zip(
                    self.oid_date[:self.oid_index_value.value], 
                    self.oid_index_code[:self.oid_index_value.value],
                    self.oid_opening_value[:self.oid_index_value.value]
                    )
                ]
            
            Clocks.oid_clock.value = False

        elif stock and not index:
            
            data_dicts = [
                {'DATE': date, 'STOCK_CODE': stock_code, 'MIN_PRICE': min_price, 'OPENING_PRICE': opening_price, 'MAX_PRICE': max_price} 
                for date, stock_code, min_price, opening_price, max_price in zip(
                    self.osd_date[:self.osd_index_value.value], 
                    self.osd_stock_code[:self.osd_index_value.value], 
                    self.osd_min_price[:self.osd_index_value.value], 
                    self.osd_opening_price[:self.osd_index_value.value], 
                    self.osd_max_price[:self.osd_index_value.value]
                    )
                ]
            
            Clocks.osd_clock.value = False
            
        session = self.Session()
        self.__opening_data_to_sql(data_dicts, session, index, stock)
        session.close()
        
        self.logger.debug("Endeks açılış değerleri veritabanına kaydedildi.")
        
        return None

    @time_interval(LoggerObjects.FTD_logger, StockExchangeTime.bist_trading_session_opening_time, DatabaseInsertionTime.bist_trading_session_insertion_time)
    def insert_current_data(self, index: bool, stock: bool) -> None:

        """
        Anlık verileri dictlere dönüştürüp veritabanına ekler.
        """

        self.logger.debug("Anlık veriler veritabanına ekleniyor.")
        
        # Veri elde etme işlemi tamamlanana dek.
        while not Clocks.tid_clock.value and not Clocks.tsd_clock.value:
            _time.sleep(1)
            
            # İnternet bağlantısının kesilmesi durumunda.
            if Clocks.conn_lost_event.value:
                self.logger.debug("FinTables sitesine bağlantı kesildi.")
                self.logger.debug("İnternet bağlantısının geri gelmesi bekleniyor.")
                
                while Clocks.conn_lost_event.value:
                    _time.sleep(3)
                    
                if _datetime.now().time() > DatabaseInsertionTime.bist_trading_session_insertion_time:
                    self.logger.debug("Borsa işlem seansı zamanı geçtiği için halihazırda elde edilmiş işlem seansı verileri veritabanına aktarılıyor.")
                    break
                
        if index and not stock:
            
            data_dicts = [
                {'DATETIME': _datetime, 'INDEX_CODE': index_code, 'VALUE': value, 'CHANGE_RATE': change_rate} 
                for _datetime, index_code, value, change_rate in zip(
                    self.tid_datetime[:self.tid_index_value.value], 
                    self.tid_index_code[:self.tid_index_value.value], 
                    self.tid_value[:self.tid_index_value.value], 
                    self.tid_change_rate[:self.tid_index_value.value]
                    )
                ]
            
            Clocks.tid_clock.value = False
            
        elif stock and not index:
            
            data_dicts = [
                {"DATETIME": stock_time, 
                    "STOCK_CODE": stock_code, 
                    "LOWEST_PRICE": lowest_price, 
                    "STOCK_PRICE": current_price, 
                    "CHANGE_RATE": change_rate, 
                    "TOTAL_TRADED_VOLUME": total_traded_volume, 
                    "TOTAL_TRADED_VALUE": total_traded_value, 
                    "HIGHEST_PRICE": highest_price
                } 
                for stock_time, stock_code, lowest_price, current_price, change_rate, total_traded_volume, total_traded_value, highest_price in zip(
                    self.tsd_datetime[:self.tsd_index_value.value], 
                    self.tsd_stock_code[:self.tsd_index_value.value], 
                    self.tsd_lowest_price[:self.tsd_index_value.value], 
                    self.tsd_current_price[:self.tsd_index_value.value], 
                    self.tsd_change_rate[:self.tsd_index_value.value], 
                    self.tsd_total_traded_volume[:self.tsd_index_value.value], 
                    self.tsd_total_traded_value[:self.tsd_index_value.value], 
                    self.tsd_highest_price[:self.tsd_index_value.value]
                    )
                ]
            
            Clocks.tsd_clock.value = False
            
        session = self.Session()
        self.__current_data_to_sql(data_dicts, session, index, stock)
        session.close()

        self.logger.debug("Anlık veriler veritabanına eklendi.")

        return None

    @time_interval(LoggerObjects.FTD_logger, StockExchangeTime.bist_exchange_closing_time, DatabaseInsertionTime.bist_closing_session_insertion_time)
    def insert_closing_data(self, index: bool, stock: bool) -> None:

        """
        Kapanış verilerini dictlere dönüştürüp veritabanına ekler.
        """
        
        self.logger.debug("Kapanış verileri veritabanına kaydediliyor.")
        
        # Veri elde etme işlemi tamamlanana dek.
        while not Clocks.cid_clock.value and not Clocks.csd_clock.value:
            _time.sleep(1)
            
            # İnternet bağlantısının kesilmesi durumunda.
            if Clocks.conn_lost_event.value:
                self.logger.debug("FinTables sitesine bağlantı kesildi.")
                self.logger.debug("İnternet bağlantısının geri gelmesi bekleniyor.")
                
                while Clocks.conn_lost_event.value:
                    _time.sleep(3)
                    
                if _datetime.now().time() > StockExchangeTime.bist_trading_session_opening_time:
                    self.logger.debug("Borsa kapanış seansı zamanı geçtiği için halihazırda elde edilmiş kapanış seansı verileri veritabanına aktarılıyor.")
                    break
                
        if index and not stock:
            
            data_dicts = [
                {'DATE': date, 'INDEX_CODE': index_code, 'CLOSING_VALUE': closing_value} 
                for date, index_code, closing_value in zip(
                    self.cid_date[:self.cid_index_value.value], 
                    self.cid_index_code[:self.cid_index_value.value], 
                    self.cid_closing_value[:self.cid_index_value.value]
                    )
                ]
            
            Clocks.cid_clock.value = False

        elif stock and not index:
            
            data_dicts = [
                {'DATE': date, 
                 'STOCK_CODE': stock_code, 
                 'CLOSING_PRICE': closing_price, 
                 'TOTAL_TRADED_VOLUME': total_traded_volume, 
                 'TOTAL_TRADED_VALUE': total_traded_value
                } 
                for date, stock_code, closing_price, total_traded_volume, total_traded_value in zip(
                    self.csd_date[:self.csd_index_value.value], 
                    self.csd_stock_code[:self.csd_index_value.value], 
                    self.csd_closing_price[:self.csd_index_value.value], 
                    self.csd_total_traded_volume[:self.csd_index_value.value], 
                    self.csd_total_traded_value[:self.csd_index_value.value]
                    )
                ]
            
            Clocks.csd_clock.value = False

        session = self.Session()
        self.__closing_data_to_sql(data_dicts, session, index, stock)
        session.close()
        
        self.logger.debug("Kapanış verileri veritabanına kaydedildi.")
        
        return None

def ft_data_to_database() -> None:
    
    ############################################################################################################
    # Veritabanına veri eklemek için kullanılan fonksiyonlar. Logger objesi ve açıklamalar eklenebilir.
    ############################################################################################################
    
    data_insert = FTInsert()
    
    with _ThreadPoolExecutor() as executor:
        
        # Veritabanı işlemleri, ayrı bir fonksiyon altında thread olarak çalıştırılabilir.
        executor.submit(data_insert.insert_opening_data)
        executor.submit(data_insert.insert_current_data)
        executor.submit(data_insert.insert_closing_data)
        
    return None

if __name__ == "__main__":
        
    pass    