import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

import numpy as np
from auxiliary.dataclass import BISTIndexData

class UpdateIndexData(BISTIndexData):
    
    @classmethod
    def update_data(cls):
        cls.index_codes.append(np.str_("XU100"))
        cls.index_values.append(np.float64(1500.0))
        cls.index_total_traded_volumes.append(np.int64(1000000))
        cls.index_total_traded_values.append(np.int64(2000000))
        cls.index_sets.append(set([np.str_("XU100")]))
        cls.all_index_stocks.add(np.str_("XU100"))
