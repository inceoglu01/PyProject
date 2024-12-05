import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

import pandas as pd

import logging
from typing import override

from loggingmodule import LoggerObjects
from dataclass import Clocks, DataBroadcastTime, StockExchangeTime, TradingStockData, TradingIndexData, OpeningStockData, OpeningIndexData, ClosingStockData, ClosingIndexData
from dataclass import OpeningDataFrames, TradingDataFrames, ClosingDataFrames

from globals import OpeningSessionColumns, TradingSessionColumns, ClosingSessionColumns

class AnalysisBase:

    """
    Analiz sınıfı. Tüm analiz sınıflarının atasıdır.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

class DynamicDataAnalysis(AnalysisBase, DataBroadcastTime, StockExchangeTime, Clocks):

    """
    Dinamik analiz sınıfı. Açılış, işlem ve kapanış seansları için ortak işlemleri yapar.
    """

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)

class OpeningSessionData(AnalysisBase, DynamicDataAnalysis, OpeningDataFrames, OpeningStockData, OpeningIndexData, OpeningSessionColumns):

    """
    Açılış seansı analiz sınıfı. Açılış seansı verilerini işler.
    """

    def __init__(self):
        super().__init__(LoggerObjects.OSA_logger)

    def data_to_dataframe(self) -> None:

        """
        Açılış seansı verilerini DataFrame nesnelerine dönüştürür.
        """

        self.logger.info("Açılış seansı DataFrame nesneleri oluşturuluyor.")

        stock_data = {
            f"{self.stock_date_column}": self.osd_date,
            f"{self.stock_code_column}": self.osd_stock_code,
            f"{self.stock_min_price_column}": self.osd_min_price,
            f"{self.stock_opening_price_column}": self.osd_opening_price,
            f"{self.stock_change_rate_column}": self.osd_change_rate,
            f"{self.stock_max_price_column}": self.osd_max_price
        }

        self.odf_stock_df = pd.DataFrame(stock_data)

        index_data = {
            f"{self.index_date_column}": self.oid_date,
            f"{self.index_code_column}": self.oid_index_code,
            f"{self.index_opening_value_column}": self.oid_opening_value,
            f"{self.index_change_rate_column}": self.oid_change_rate
        }

        self.odf_index_df = pd.DataFrame(index_data)

        self.logger.info("Açılış seansı DataFrame nesneleri oluşturuldu.")

        return None
    
class TradingSessionData(AnalysisBase, DynamicDataAnalysis, TradingDataFrames, TradingStockData, TradingIndexData, TradingSessionColumns):

    """
    Sürekli işlem seansı analiz sınıfı. İşlem seansı verilerini işler.
    """

    def __init__(self):
        super().__init__(LoggerObjects.TSA_logger)

    def data_to_dataframe(self) -> None:
        
        """
        İşlem seansı verilerini DataFrame nesnelerine dönüştürür.
        """
        
        self.logger.info("İşlem seansı DataFrame nesneleri oluşturuluyor.")
        
        if self.data_clock:
        
            stock_data = {
                f"{self.stock_datetime_column}": self.tsd_datetime,
                f"{self.stock_code_column}": self.tsd_stock_code,
                f"{self.stock_lowest_price_column}": self.tsd_lowest_price,
                f"{self.stock_current_price_column}": self.tsd_current_price,
                f"{self.stock_change_rate_column}": self.tsd_change_rate,
                f"{self.stock_highest_price_column}": self.tsd_highest_price,
                f"{self.stock_traded_volume_column}": self.tsd_total_traded_volume,
                f"{self.stock_traded_value_column}": self.tsd_total_traded_value
            }

            self.__class__.tdf_stock_df = pd.DataFrame(stock_data)
            
            index_data = {
                f"{self.index_datetime_column}": self.tid_datetime,
                f"{self.index_code_column}": self.tid_index_code,
                f"{self.index_current_value_column}": self.tid_value,
                f"{self.index_change_rate_column}": self.tid_change_rate
            }
            
            self.__class__.tdf_index_df = pd.DataFrame(index_data)
            
            self.logger.info("İşlem seansı DataFrame nesneleri oluşturuldu.")

        return None
    
    def update_stock_data(self) -> None:
        
        """
        İşlem seansı hisse verilerini günceller.
        """
        
        if self.data_clock:
            self.logger.info("İşlem seansı verileri güncelleniyor.")
            
            stock_data = {
                f"{self.stock_datetime_column}": self.tsd_datetime[-30:],
                f"{self.stock_code_column}": self.tsd_stock_code[-30:],
                f"{self.stock_lowest_price_column}": self.tsd_lowest_price[-30:],
                f"{self.stock_current_price_column}": self.tsd_current_price[-30:],
                f"{self.stock_change_rate_column}": self.tsd_change_rate[-30:],
                f"{self.stock_highest_price_column}": self.tsd_highest_price[-30:],
                f"{self.stock_traded_volume_column}": self.tsd_total_traded_volume[-30:],
                f"{self.stock_traded_value_column}": self.tsd_total_traded_value[-30:]
            }
            
            new_df = pd.DataFrame(stock_data)
            
            self.__class__.tdf_stock_df = pd.concat([self.tdf_stock_df, new_df], ignore_index=True)
            
            self.logger.info("İşlem seansı verileri güncellendi.")
        
        return None
    
    def update_index_data(self) -> None:
        
        """
        İşlem seansı endeks verilerini günceller.
        """
        
        if self.data_clock:
            self.logger.info("İşlem seansı verileri güncelleniyor.")
            
            index_data = {
                f"{self.index_datetime_column}": self.tid_datetime[-2:],
                f"{self.index_code_column}": self.tid_index_code[-2:],
                f"{self.index_current_value_column}": self.tid_value[-2:],
                f"{self.index_change_rate_column}": self.tid_change_rate[-2:]
            }
            
            new_df = pd.DataFrame(index_data)
            
            self.__class__.tdf_index_df = pd.concat([self.tdf_index_df, new_df], ignore_index=True)
            
            self.logger.info("İşlem seansı verileri güncellendi.")
            
        return None
            
class ClosingSessionData(AnalysisBase, DynamicDataAnalysis, ClosingDataFrames, ClosingStockData, ClosingIndexData, ClosingSessionColumns):

    """
    Kapanış seansı analiz sınıfı. Kapanış seansı verilerini işler.
    """

    def __init__(self):
        super().__init__(LoggerObjects.CSA_logger)

    def data_to_dataframe(self) -> None:
        
        """
        Kapanış seansı verilerini DataFrame nesnelerine dönüştürür.
        """
        
        self.logger.info("Kapanış seansı DataFrame nesneleri oluşturuluyor.")
        
        stock_data = {
            f"{self.stock_date_column}": self.csd_date,
            f"{self.stock_code_column}": self.csd_stock_code,
            f"{self.stock_closing_price_column}": self.csd_closing_price,
            f"{self.stock_change_rate_column}": self.csd_change_rate,
            f"{self.stock_traded_volume_column}": self.csd_total_traded_volume,
            f"{self.stock_traded_value_column}": self.csd_total_traded_value
        }
        
        self.__class__.cdf_stock_df = pd.DataFrame(stock_data)
        
        index_data = {
            f"{self.index_date_column}": self.cid_date,
            f"{self.index_code_column}": self.cid_index_code,
            f"{self.index_closing_value_column}": self.cid_closing_value,
            f"{self.index_change_rate_column}": self.cid_change_rate
        }
        
        self.__class__.cdf_index_df = pd.DataFrame(index_data)
        
        self.logger.info("Kapanış seansı DataFrame nesneleri oluşturuldu.")
        
        return None
