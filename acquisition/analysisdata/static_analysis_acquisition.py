import sys
import os

import pandas as pd

from database.acquisition.historical_database import DSHistoricalQuery

####################################################################################################
# Static Analysis Acquisition
# Veriler veritabanından çekilip işlenir ve analiz edilir.
####################################################################################################

class StaticAnalysisAcquisition(DSHistoricalQuery):
    
    def __init__(self):
        super().__init__()
