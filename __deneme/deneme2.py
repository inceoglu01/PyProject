import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

from auxiliary.dataclass import BISTIndexData

class ReadIndexData(BISTIndexData):
    
    @classmethod
    def read_data(cls):
        print("Index Codes:", cls.index_codes)
        print("Index Values:", cls.index_values)
        print("Total Traded Volumes:", cls.index_total_traded_volumes)
        print("Total Traded Values:", cls.index_total_traded_values)
        print("Index Sets:", cls.index_sets)
        print("All Index Stocks:", cls.all_index_stocks)
