import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

from loggingmodule import LoggerObjects as _LoggerObjects
from errorhandling import ErrorHandling, SQLAlchemyErrorHandling
from dataclass import BISTIndexData

from sqlalchemy import MetaData, and_
from database.database import create_db_engine, HistoricalDatabase, DatabaseTables, DatabaseNames, XU030, XU100

from sqlalchemy.sql.functions import func
from datetime import datetime as _datetime, timedelta as _timedelta

from typing import override

import pandas as pd
import numpy as _np

"""
Tarihsel verilerin veritabanına yazılması, istenildiği zaman verilerin çekilmesi
ve veritabanındaki verilerin güncellenmesi işlemlerini gerçekleştiren modül.
"""

class DSHistoricalDatabase(HistoricalDatabase):
    
    """
    DSHistoricalDatabase sınıfı, DataStore sitesinden elde edilen tarihsel verileri veritabanına yazmak için gerekli değişken ve metodları içerir.
    """
    
    HD_engine = create_db_engine(DatabaseNames.bist_historical_data_db)
            
    def __init__(self) -> None:
        super().__init__(self.HD_engine, MetaData(), _LoggerObjects.DSD_logger)

class DSQuery(DSHistoricalDatabase, BISTIndexData):

    """
    DSQuery sınıfı, DataStore sitesinden elde edilen tarihsel verileri veritabanından çekmek için gerekli değişken ve metodları içerir.
    """

    ####################################################################################################
    # Veritabanından veri okur.
    # Sorgulanacak veritabanı tabloları sabit olmakla birlikte
    # sorgu değişken olabilir. Örneğin, tarih aralığına göre sorgu yapılabilir.
    # Sorgu sonucu dönen veri DataFrame olarak döner.
    # Sorgu sonuçlarının analiz modülüyle nasıl paylaşılabileceği araştırılmalıdır.
    ####################################################################################################
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DSQuery, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
                
    # Tarih formatını düzenleme
    @ErrorHandling.unexpected_error(logger= _LoggerObjects.DSD_logger, gmessage= "Tarih formatı düzenlenemedi.", exit= True)
    def __time_normalization(self, table_name: str, latest_date: _datetime) -> str:
            
        """
        Belirtilen tablodan alınan son tarih verisinin formatını düzenler, işleme uygun hale getirir.
        """

        if table_name == DatabaseTables.datastore_h_stock:
            if latest_date == None:
                latest_date = "01-08-2020"
            else:
                latest_date = _timedelta(days=36) + latest_date
                latest_date = _datetime.strftime(latest_date, "%d-%m-%Y")
        elif table_name == DatabaseTables.datastore_h_index:
            if latest_date == None:
                latest_date = "01-08-2020"
            else:
                latest_date = _timedelta(days=36) + latest_date
                latest_date = _datetime.strftime(latest_date, "%d-%m-%Y")
        elif table_name == DatabaseTables.datastore_c_stock_index:
            if latest_date == None:
                latest_date = "01-08-2020"
            else:
                latest_date = latest_date
                latest_date = _datetime.strftime(latest_date, "%d-%m-%Y")
        elif table_name == DatabaseTables.datastore_h_volatility:
            if latest_date == None:
                latest_date = "01-08-2020"
            else:
                latest_date = _timedelta(days=1) + latest_date
                latest_date = _datetime.strftime(latest_date, "%d-%m-%Y")
        elif table_name == DatabaseTables.datastore_h_stock_index:
            if latest_date == None:
                latest_date = "01-08-2020"
            else:
                latest_date = _datetime.strptime(str(latest_date + 1), "%Y")
                latest_date = _datetime.strftime(latest_date, "%d-%m-%Y")
        else:
            self.logger.error(f"Geçersiz tablo ismi. Tablo ismi: {table_name}")
    
        return latest_date
    
    # En son tarihi elde etme
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DSD_logger, emessage= "En son tarih elde edilemedi.",  gmessage= "En son tarih elde edilemedi.", exit= False)
    def get_latest_date(self, table_name: str) -> str | None:

        """
        Belirtilen veritabanındaki belirtilen tablodaki en son tarihi elde eder.
        """

        # Tablo sütunlarını al
        columns = self.get_table_columns(table_name)

        for column in columns:
            # DATE veya DATETIME sütun ismi tarih sütunu olarak kabul edilir. Tarihle ilgili olmayan sütunlarda DATE ifadesi kullanılmamalıdır.
            if "DATE" in column[0]: 
                date_column = column[1]
                break
            else:
                return None

        try:
            self.create_session
            raw_latest_date = self.last_session.query(func.max(date_column)).scalar()
            self.commit_session
            
        except Exception as e:
            self.logger.error(f"En son tarih elde edilirken beklenmeyen bir hata oluştu. Hata: {e}")
            self.rollback_session
            return None
        
        finally:
            self.close_session
            
        latest_date = self.__time_normalization(table_name, raw_latest_date)

        return latest_date

    # Satır sayısını elde etme
    @override
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DSD_logger, emessage= "Satır sayısı elde edilemedi.",  gmessage= "Satır sayısı elde edilemedi.", exit= False)
    def get_row_length(self, table_type) -> list[int] | None:
            
        """
        Belirtilen veritabanındaki belirtilen tablodaki satır sayısını elde eder.
        """

        if table_type == DatabaseTables.datastore_h_volatility:
            table = self.get_table_object(table_type)
            try:
                self.create_session
                row_count_030 = self.last_session.query(table).filter(table.c.INDEX_CODE == XU030).count()
                row_count_100 = self.last_session.query(table).filter(table.c.INDEX_CODE == XU100).count()
                row_count = [row_count_030, row_count_100]
                self.commit_session
                
            except Exception as e:
                self.logger.error(f"Satır sayısı elde edilirken beklenmeyen bir hata oluştu. Hata: {e}")
                self.rollback_session
                return None
            
            finally:
                self.close_session
                
        else:
            self.logger.error("Geçersiz tablo ismi.")
            return None

        return row_count

    # Belirtilen tarihe ilişkin endeks kodlarını elde eder.
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DSD_logger, emessage= "Endeks kodları elde edilemedi.",  gmessage= "Endeks kodları elde edilemedi.", exit= False)
    def get_index_codes(self, date: str = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d")) -> list[str] | None:
        
        """
        DS_C_STOCK_INDEX tablosundaki belirtilen güne ait endeks kodlarını elde eder.
        
        date: str -> Tarih. Belirtilen tarihe ait endeks kodlarını elde etmek için kullanılır.
        """
        
        #################################################################################
        #   !!!<GELİŞTİRİLECEK>!!!
        #   İleriye dönük olarak analizlerden gelen veriler sonucunda izlenilmesi gereken
        #   endekslerin belirlenmesi sonucu ve veri elde etme işlemlerinin bu
        #   endekslere dahil hisseler üzerinden yapılması sağlanabilir.
        #   Bu durumda get_index_codes fonksiyonu get_all_stock_codes fonksiyonu ile birleştirilebilir.
        #   Max takip edilebilecek hisse sayısına göre ekstra bir kontrol yapılabilir ve
        #   sonuç buna göre düzenlenebilir.
        #   !!!<GELİŞTİRİLECEK>!!!
        #################################################################################
        
        table = self.get_table_object(DatabaseTables.datastore_c_stock_index) # Tablo ön tanımlı fakat dinamik hale getirilebilir.
        
        try:
            self.create_session
            index_code_rows = self.last_session.query(table.c.INDEX_CODE).filter(table.c.DATE == date).distinct().all()
            self.commit_session
            
        except Exception as e:
            self.logger.error(f"Endeks kodları elde edilirken beklenmeyen bir hata oluştu. Hata: {e}")
            self.rollback_session
            return None
        
        finally:
            self.close_session
            
        index_code_set : set[str] = {row[0] for row in index_code_rows}
        index_code_list = sorted(index_code_set)
        
        return index_code_list
            
    # Belirtilen tarihteki hisse kodlarını istenen endekse bağlı olarak elde etme
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DSD_logger, emessage= "Hisse kodları elde edilemedi.",  gmessage= "Hisse kodları elde edilemedi.", exit= False)
    def get_all_stock_codes(self, index_codes: list[str] | tuple[str] = [XU030, XU100], start_date: str = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d"), end_date: str = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d")) -> None:
        
        """
        DS_C_STOCK_INDEX tablosundaki belirtilen endekse ve tarih aralığına ait hisse kodlarını benzersiz şekilde elde eder.
        """

        table = self.get_table_object(DatabaseTables.datastore_c_stock_index) # Tablo ön tanımlı fakat dinamik hale getirilebilir.

        try:
            self.create_session
            stock_rows = self.last_session.query(table.c.STOCK_CODE).filter(and_(table.c.INDEX_CODE.in_(index_codes), table.c.DATE >= start_date, table.c.DATE <= end_date)).all()
            self.commit_session
            
        except Exception as e:
            self.logger.error(f"Hisse kodları elde edilirken beklenmeyen bir hata oluştu. Hata: {e}")
            self.rollback_session
            return None
        
        finally:
            self.close_session
            
        stock_set: set[_np.str_] = {_np.str_(row[0]) for row in stock_rows} # Tekrar eden hisse kodlarını kaldırır.
        self.assign_all_index_stocks(stock_set)
        
        return None

    # Belirtilen tarihteki endeks-hisse çifti verilerini birlikte elde etme
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DSD_logger, emessage= "Endeks-hisse verileri elde edilemedi.",  gmessage= "Endeks-hisse verileri edilemedi.", exit= False)
    def get_index_stock_datas(self, index_codes: list[str] | tuple[str] = [XU030, XU100], date: str = _datetime.strftime(_datetime.now().date(), "%Y-%m-%d")) -> None:
        
        """
        DS_C_STOCK_INDEX tablosundaki belirtilen endeks ve tarihe ait endeks-hisse çifti verilerini benzersiz şekilde elde eder.
        """

        table = self.get_table_object(DatabaseTables.datastore_c_stock_index) # Tablo ön tanımlı fakat dinamik hale getirilebilir.
        
        try:
            self.create_session
            for index_code in index_codes:
                stock_rows = self.last_session.query(table.c.STOCK_CODE).filter(and_(table.c.INDEX_CODE == index_code, table.c.DATE == date)).all()
                stock_set: set[_np.str_] = {_np.str_(row[0]) for row in stock_rows} # Tekrar eden hisse kodlarını kaldırır.
                self.append_index_codes(_np.str_(index_code))
                self.append_index_sets(stock_set)
                self.append_index_total_traded_volumes(_np.int64(0))
                self.append_index_total_traded_values(_np.int64(0))
            self.commit_session
            
        except Exception as e:
            self.logger.error(f"Endeks-hisse verileri elde edilirken beklenmeyen bir hata oluştu. Hata: {e}")
            self.rollback_session
            return None
        
        finally:
            self.close_session
            
        return None

class DSInsert(DSHistoricalDatabase):

    ####################################################################################################
    # Veritabanına veri yazar.
    # Veritabanına yazılacak veri DataFrame olarak gelir.
    # Veritabanına yazma işlemi gerçekleşirse True döner.
    # Gerçekleşmezse False döner.
    # Veritabanına yazılacak veriler değişkendir, bu nedenle
    # gelen verilerin önceden belirlenmeksizin dinamik bir şekilde
    # veritabanına yazılması sağlanmalıdır.
    ####################################################################################################
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DSInsert, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
            
    # DataFrame nesnesinin boş olup olmadığını kontrol eder
    def __is_empty_df(self, df: pd.DataFrame) -> bool:
            
        """
        DataFrame nesnesinin boş olup olmadığını kontrol eder.
        """

        @ErrorHandling.unexpected_error(logger= self.logger, gmessage= "DataFrame nesnesi doğruluk değeri kontrol edilemedi.", exit= True)
        def is_empty_df(df: pd.DataFrame) -> bool:

            self.logger.debug("Boş DataFrame kontrol fonksiyonu çalıştırılıyor.")
            try:
                if df == None:
                    self.logger.debug("Tabloya eklenecek veri bulunamadı.")
                    return False

                if df.empty:
                    self.logger.debug("Tabloya eklenecek veri bulunamadı.")
                    return False
                
            except Exception as e:
                self.logger.debug("DataFrame nesnesi doğruluk değeri belirsiz.")
                self.logger.debug(f"{e}")

            finally:
                self.logger.debug("Boş DataFrame kontrolü tamamlandı.")

            return True
        
        return is_empty_df(df)
    
    # DataFrame'deki verileri belirtilen tabloya ekler
    def df_to_sql(self, df: pd.DataFrame, table_name: str) -> None:
        
        """
        Veri tabanına DataFrame nesnesindeki verileri ekler.
        """

        @ErrorHandling.unexpected_error(logger= self.logger, gmessage= "DataFrame tabloya eklenemedi.", exit= True)
        def df_to_sql(df: pd.DataFrame, table_name: str) -> None:

            self.logger.debug("DataFrame tabloya ekleme fonksiyonu çalıştırılıyor.")

            is_empty = self.__is_empty_df(df)
            if is_empty == False:
                return None

            session = self.Session() # Oturum oluştur

            df.to_sql(table_name, self.engine, if_exists='append', index=False) # Veriyi tabloya ekle
            self.logger.debug(f"DataFrame tabloya eklendi. Tablo adı: {table_name}")

            session.commit()
            session.close()

            self.logger.debug("Aktarım işlemi başarıyla tamamlandı!")

            return None
        
        return df_to_sql(df, table_name)

    def write_to_database(self, df_list: list) -> None:

        df_ceh = df_list[0]
        df_ev = df_list[1]

        self.VT_logger.debug("Anlık Veri Tabanı modülü başlatıldı.")
        self.vt_obj.df_to_sql(df_ceh, DatabaseTables.datastore_c_stock_index) # Cari Endeks Hisse verilerini veritabanına yazar.
        self.vt_obj.df_to_sql(df_ev, DatabaseTables.datastore_h_volatility) # Endeks Volatilite verilerini veritabanına yazar.
        self.VT_logger.debug("Anlık Veri Tabanı modülü tamamlandı.")

        return None

class DSDatabaseManager:
    
    """
    DSDatabasePool sınıfı, veritabanı işlemlerinin gerçekleştirildiği sınıfların örneklerini oluşturur.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DSDatabaseManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.insert = DSInsert()
            self.query = DSQuery()
            self.logger = _LoggerObjects.DSD_logger

if __name__ == "__main__":
        
    dspool = DSDatabaseManager()
    
    DATETIME = "2024-06-24"
    
    all_index_codes = dspool.query.get_index_codes(DATETIME)
    dspool.query.get_all_stock_codes([XU030, XU100], DATETIME, DATETIME)
    dspool.query.get_index_stock_datas([XU030, XU100], DATETIME)
    
    print(len(DSQuery.all_index_stocks))
    print(len(BISTIndexData.index_codes))
    print(len(BISTIndexData.index_sets))
    