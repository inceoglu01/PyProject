import sqlalchemy as db
from sqlalchemy import MetaData, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import SQLAlchemyError

import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Program dosyalarının bulunduğu ana dizin eklenir.

from auxiliary.globals import DatabaseNames, DatabaseTables, conn_string
from logging import Logger as _Logger
from auxiliary.errorhandling import SQLAlchemyErrorHandling

# Endeks isimleri
XU030 = "XU030"
XU100 = "XU100"

"""
Veri Tabanı Modülü
"""

from auxiliary.loggingmodule import LoggerObjects as _LoggerObjects

@SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DBB_logger, emessage= "SQL Server bağlantısı sağlanamadı.", gmessage= "SQL Server bağlantısı sağlanamadı.", exit= True)
def create_db_engine(db_name: str = "master") -> Engine | None:

    """
    SQL Server bağlantısı için kullanılan engine nesnesini döndürür.
    """
    conn = conn_string(db_name)

    if conn is not None:
        engine = db.create_engine(conn)
        return engine
    else:
        return None
        
class DatabaseBase:

    """
    DatabaseBase sınıfı, RDBMS veritabanları için ortak olan temel değişken ve metodları içerir.
    """

    # Tanımlamalar
    def __init__(self, engine: Engine, metadata: MetaData, logger: _Logger) -> None:
        self.engine = engine
        self.metadata = metadata
        self.reflect_metadata()
        self.Sessionmaker = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.logger = logger
        self._sessions : list[Session] = []

    # Veritabanı tablolarını yansıtma
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DBB_logger, emessage= "Veritabanı bağlantısı sağlanamadı.", gmessage= "Veritabanı bağlantısı sağlanamadı.", exit= True)
    def reflect_metadata(self):
            
        """
        Veritabanındaki tabloları yansıtır.
        """
        
        self.metadata.reflect(bind=self.engine)
        
        return None
    
    # Yeni session oluşturma
    @property
    def create_session(self) -> Session:
        
        """
        Yeni bir session nesnesi oluşturur ve oluşturuğu session nesnesini döndürür.
        """
        
        session = self.Sessionmaker()
        self._sessions.append(session)
        
        return session

    # Son sessionı kaydetme
    @property
    def commit_session(self) -> None:
            
        """
        Son sessionı kaydeder.
        """
        self.last_session.commit()        
        
        return None
    
    # Son sessionı geri alma
    @property
    def rollback_session(self) -> None:
            
        """
        Son sessionı geri alır.
        """
        self.last_session.rollback()
                
        return None

    @property
    def close_session(self) -> None:
            
        """
        Son sessionı kapatır.
        """
        
        self.last_session.close()
        self._sessions.remove(self.last_session)
                
        return None

    # Son sessiona erişim
    @property
    def last_session(self) -> Session | None:
        
        """
        Son session nesnesine erişim sağlar.
        """
        
        return self._sessions[-1]

    # Veritabanı tablo isimlerini elde etme
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DBB_logger, emessage= "Veritabanı tablo isimleri elde edilemedi.", gmessage= "Veritabanı tablo isimleri elde edilemedi.", exit= True)
    def get_table_names(self) -> list[str]:

        """
        Veritabanındaki tablo isimlerini elde eder.
        """
        
        table_names = self.metadata.tables.keys()
        
        return list(table_names)

    # Tablo nesnesi oluşturma
    @SQLAlchemyErrorHandling.nosuchtable_error(logger= _LoggerObjects.DBB_logger, emessage= "Tablo nesnesi oluşturulamadı.", gmessage= "Tablo nesnesi oluşturulamadı.", exit= True)
    def get_table_object(self, table_name: str) -> db.Table | None:

        """
        Belirtilen veritabanındaki belirtilen tablo nesnesini elde eder.
        """

        if table_name in DatabaseTables.get_table_list():
            pass

        else:
            return None

        table = db.Table(table_name, self.metadata, autoload_with=self.engine)

        return table
    
    # Belirtilen tablodaki kolon isimlerini ve nesnelerini elde etme
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DBB_logger, emessage= "Kolon bilgileri elde edilemedi.", gmessage= "Kolon bilgileri elde edilemedi.", exit= True)
    def get_table_columns(self, table_name: str) -> list[tuple[str, db.Column]]:
            
        """
        Belirtilen veritabanındaki belirtilen tablonun kolon isimlerini ve nesnelerini elde eder.
        """

        # Tablo nesnesini al
        table = self.get_table_object(table_name)

        # Kolon isimlerini al
        columns = table.columns.items()

        return columns
    
    # Satır sayısını elde etme
    @SQLAlchemyErrorHandling.sqlalchemy_error(logger= _LoggerObjects.DBB_logger, emessage= "Satır sayısı elde edilemedi.", gmessage= "Satır sayısı elde edilemedi.", exit= True)
    def get_row_length(self, table_name: str) -> int:
            
        """
        Belirtilen veritabanındaki belirtilen tablodaki satır sayısını elde eder.
        """

        table = self.get_table_object(table_name)

        try:
            self.create_session
            row_count = self.last_session.query(table).count()
            self.commit_session
            return row_count
            
        except SQLAlchemyError as e:
            self.logger.error(f"Satır sayısı elde edilirken beklenmeyen bir SQLAlchemy hatası oluştu. Hata: {e}")
            self.rollback_session
            return None
        
        except Exception as e:
            self.logger.error(f"Satır sayısı elde edilirken beklenmeyen bir hata oluştu. Hata: {e}")
            self.rollback_session
            return None
        
        finally:
            self.close_session

class HistoricalDatabase(DatabaseBase):

    """
    HistoricalDatabase sınıfı, tarihsel verileri veritabanına yazmak için gerekli ortak değişken ve metodları içerir.
    """

    # Tanımlamalar
    def __init__(self, engine: Engine, metadata: MetaData, logger: _Logger) -> None:
        super().__init__(engine, metadata, logger)

class CurrentDatabase(DatabaseBase):

    """
    CurrentDatabase sınıfı, anlık verileri veritabanına yazmak için gerekli ortak değişken ve metodları içerir.
    """

    # Tanımlamalar
    def __init__(self, engine: Engine, metadata: MetaData, logger: _Logger) -> None:
        super().__init__(engine, metadata, logger)
    
if __name__ == "__main__":
    
    # Veritabanı engine nesnesi oluşturulur.
    engine = create_db_engine(DatabaseNames.program_db)
    
    # Veritabanı metadata nesnesi oluşturulur.
    metadata = MetaData()
    
    # Logger nesnesi oluşturulur.
    logger = _LoggerObjects.DBB_logger
    
    # HistoricalDatabase nesnesi oluşturulur.
    historical_db = HistoricalDatabase(engine, metadata, logger)
    
    # CurrentDatabase nesnesi oluşturulur.
    current_db = CurrentDatabase(engine, metadata, logger)
    
    # HistoricalDatabase nesnesi ile veritabanındaki tablo isimleri alınır.
    print(historical_db.get_table_names())
    
    # HistoricalDatabase nesnesi ile veritabanındaki tablo nesneleri alınır.
    print(historical_db.get_table_object(DatabaseTables.logs), "\n")
    
    # HistoricalDatabase nesnesi ile veritabanındaki tablo kolonları alınır.
    print(historical_db.get_table_columns(DatabaseTables.logs) , "\n")
    
    # HistoricalDatabase nesnesi ile veritabanındaki tablo satır sayısı alınır.
    print(historical_db.get_row_length(DatabaseTables.logs), "\n")
    
    # CurrentDatabase nesnesi ile veritabanındaki tablo isimleri alınır.
    print(current_db.get_table_names(), "\n")
    
    # CurrentDatabase nesnesi ile veritabanındaki tablo nesneleri alınır.
    print(current_db.get_table_object(DatabaseTables.logs), "\n")
    
    # CurrentDatabase nesnesi ile veritabanındaki tablo kolonları alınır.
    print(current_db.get_table_columns(DatabaseTables.logs), "\n")
    
    # CurrentDatabase nesnesi ile veritabanındaki tablo satır sayısı alınır.
    print(current_db.get_row_length(DatabaseTables.logs), "\n")
