import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.

import logging
import pandas as pd
import os
import sys
from zipfile import ZipFile

from globals import DSFileNames, Dtypes, Paths, ColumnNames, conn_string, DatabaseNames, Deletables, FileExtensions
from errorhandling import ErrorHandling
from dataclass import DSFileData, DSDataFrames

from database.database import HistoricalDataModul, DatabaseTables
from sqlalchemy import create_engine, MetaData
from loggingmodule import LoggerObjects, info, debug, warning, error, critical

from analysis.analysis import AnalysisBase

class DSFormalization(AnalysisBase, Paths, DSFileNames, DSFileData, FileExtensions, DSDataFrames):

    def __init__(self):
        super().__init__(LoggerObjects.DSFo_logger)
        
    # İndirilen dosya bilgilerini alır ve bir sözlükte saklar. !!!DOSYA VERİLERİ ELDE ETME MODÜLÜ GÜNCELLENECEK!!!
    def __get_file_info(self, file_string: str, unzipped_files: bool = False) -> None:

        """
        İndirilen dosya bilgilerini alır ve bir sözlükte saklar.
        """

        def get_file_dates(file: str) -> None:

            """
            Dosya ismi içindeki tarihi alır.
            """

            try:
                self.__class__.file_dates.append(file.split(".")[2]) # Dosyanın tarihini listeye ekler. Endeks Hacim ve Endeks Volatilite dosyaları için.

            except:
                self.logger.debug(f"Dosya tarihi alınamadı. Ayraç '.' değil. Dosya ismi: {file}")
                self.logger.debug("Dosya tarihi tekrar alınıyor. Ayraç '_' olarak değiştirildi.")
                try:
                    self.__class__.file_dates.append((file.split("_")[3]).split(".")[0]) # Dosyanın tarihini listeye ekler. Hisse Fiyat Hacim ve Cari Endeks Hisse dosyaları için.
                    self.logger.debug(f"Dosya tarihi alındı. Dosya ismi: {file}")

                except:
                    self.logger.debug(f"Dosya tarihi alınamadı. Dosya ismi: {file}")
                    self.logger.debug("Dosya tarihi tekrar alınıyor.")
                    try:
                        self.__class__.file_dates.append((file.split(".")[0])[-4:]) # Dosyanın tarihini listeye ekler. Eski Endeks dosyaları için.
                        self.logger.debug(f"Dosya tarihi alındı. Dosya ismi: {file}")

                    except:
                        self.logger.warning(f"Dosya tarihi alınamadı. Standart değer atanıyor. Dosya ismi: {file}")
                        self.__class__.file_dates.append("0") # Standart değer: 0
                        
            return None

        @ErrorHandling.unexpected_error(logger=self.logger, gmessage= "Dosya isimleri elde etme metodu çalıştırılamadı.", exit= True)
        def get_file_info(file_string: str, unzipped_files: bool = False) -> None:

            # Dosya isimlerini indirme klasöründen elde eder.
            self.logger.debug("Dosya isimleri elde etme metodu başlatılıyor.")
            self.logger.debug("Dosya isimleri elde ediliyor.")
            dir_file_names = os.listdir(self.indirme_dir)
            self.logger.debug("Dosya isimleri alındı.")

            # Dosya yolunda herhangi bir dosya yoksa çıkış yapar.
            if dir_file_names == []:
                self.logger.warning("Belirtilen klasörde herhangi bir dosya bulunamadı.")
                return None

            # Dosya isimlerini filtreler.
            self.logger.debug("Dosya isimleri filtreleniyor.")
            for file_name in dir_file_names:
                
                if not unzipped_files:
                
                    if file_string in file_name:
                        self.logger.debug(f"Dosya bilgileri alınıyor. Dosya ismi: {file_name}")
                        self.__class__.file_names.append(file_name) # Dosyanın adını uzantısıyla birlikte listeye ekler.
                        self.__class__.file_paths.append(os.path.join(self.indirme_dir, file_name))
                        self.__class__.table_names.append(os.path.splitext(file_name)) # Dosyanın adını uzantısız olarak listeye ekler.
                        get_file_dates(file_name) # Dosyanın tarihini alır.
                        self.logger.debug("Dosya bilgileri alındı.")
                        
                elif unzipped_files:
                    
                    if file_string in file_name:
                        self.logger.debug(f"Dosya bilgileri alınıyor. Dosya ismi: {file_name}")
                        self.__class__.unzipped_file_names.append(file_name)
                        self.__class__.unzipped_file_paths.append(os.path.join(self.indirme_dir, file_name))
                        get_file_dates(file_name)
                        self.logger.debug("Dosya bilgileri alındı.")
                        
                else:
                    raise ValueError("Geçersiz argüman. unzipped argümanının değeri bool olmalı. Dosya bilgileri alınamadı.")
                    sys.exit(1)

            # Dosya ismi bulunamazsa
            if self.file_names == []:
                self.logger.debug("Dosya ismi filtreleme işlemi tamamlandı.")
                self.logger.warning("Dosya ismi bulunamadı.")
                self.logger.debug("Dosya isimleri elde etme metodu tamamlandı.")
                return None
            
            self.logger.debug("Dosya isimleri filtreleme işlemi tamamlandı.")
            self.logger.debug("Dosya isimleri elde etme metodu tamamlandı.")
            return None
        
        return get_file_info(file_string, unzipped_files)
    
    # ZIP dosyası içindeki dosyaları çıkarır ve ismini düzenler. !!!HATA VAR, METOD YENİDEN YAZILACAK!!!
    def __unzip_files(self, file_name: str) -> tuple:

        """
        ZIP dosyası içindeki dosyaları çıkarır ve ismini düzenler.
        
        PATH STRİNG BİRLEŞTİRME YÖNTEMLERİ GÖZDEN GEÇİRİLECEK. ZIP ÇIKARMA YÖNTEMLERİ GÖZDEN GEÇİRİLECEK.
        ÇIKARILMIŞ DOSYALARIN YOLUNA İLİŞKİN KONTROL YAPILACAK.
        """

        @ErrorHandling.unexpected_error(self.logger, gmessage= "Dosya çıkarma işlemi yapılamadı.", exit= True)
        def unzip_files(file_name: str) -> tuple:
            i = 0
            path_list = []
            name_list = []

            self.logger.debug("Dosya çıkarma işlemi başlatılıyor...")
            for path in self.file_paths:

                # Belirtilen uzantıya sahip dosyaları çıkarmaz. 1. kontrol noktası.
                if self.ZIP in path:
                    self.logger.debug(f"Dosya çıkarma işlemi yapılıyor. Dosya adı: {self.file_names[i]}")

                else:
                    i += 1
                    continue

                # Dosya ismine göre çıkarma işlemi gerçekleştirir.
                if file_name == self.ESKIENDEKS:

                    # ZIP dosyası içindeki tüm dosyaları çıkarır.
                    ZipFile(path).extractall(path = self.indirme_dir)
                    self.logger.debug(f"Dosya çıkarma işlemi yapıldı. Dosya adı: {self.file_names[i]}")

                    # Çıkarılan dosyaların bilgilerini alır.
                    self.logger.debug("Çıkarılan dosyaların bilgileri alınıyor...")
                    self.__get_file_info(self.XLSX, unzipped_files=True)
                    self.logger.debug("Çıkarılan dosyaların bilgileri alındı.")

                elif file_name == self.ENDEKSHACIM:

                    # Dosyanın çıkarılma ismi kontrol edilir. 2. kontrol noktası.
                    if not os.path.exists(os.path.join(self.indirme_dir, self.UNZIPPED_ENDEKSHACIM)):
                        ZipFile(path).extract(self.UNZIPPED_ENDEKSHACIM, path = self.indirme_dir)
                        self.logger.debug(f"Dosya çıkarma işlemi yapıldı. Çıkarılan dosyanın adı: {self.file_names[i]}")
                        
                    else:
                        self.logger.debug(f"Dosya halihazırda çıkarılmış. Dosya çıkarma işlemi yapılmadı. Çıkarılmak istenen dosyanın adı: {self.file_names[i]}")
                        i += 1
                        continue

                    # Çıkarılan dosyanın yolu alınır.
                    self.logger.debug("Çıkarılan dosyanın yolu alınıyor...")
                    unzipped_file_path = self.indirme_dir + "\\" + self.UNZIPPED_ENDEKSHACIM # Çıkarılan dosyanın tam yolunu alır.
                    self.logger.debug(f"Çıkarılan dosyanın yolu alındı. Dosyanın tam yolu: {unzipped_file_path.split("\\")[-1]}")

                    # Çıkarılan dosyanın ismi düzenlenir.
                    self.logger.debug("Çıkarılan dosyanın ismi düzenleniyor...")
                    new_path = unzipped_file_path.split(".")[0] + "_" + self.file_dates[i] + self.CSV # Çıkarılan dosyanın ismini düzenler.
                    self.__class__.unzipped_file_paths.append(new_path) # Dosyanın yeni yolunu listeye ekler.
                    self.logger.debug(f"Çıkarılan dosyanın ismi düzenlendi. Yeni dosya tam ismi: {new_path.split("\\")[-1]}")

                    # Dosya ismi düzenleme işlemi yapar. Eğer dosya ismi düzenlenen dosya ismiyle aynıysa işlem yapmaz. 3. kontrol noktası.
                    if not os.path.exists(new_path):
                        os.rename(unzipped_file_path, new_path)
                        self.logger.debug(f"Çıkarılan dosyanın ismi düzenlendi. Yeni dosya ismi: {new_path.split("\\")[-1]}")
                        
                    else:
                        self.logger.debug(f"Dosya halihazırda bulunuyor. Dosya ismi düzenleme işlemi yapılmadı. Yeni dosya ismi: {new_path.split("\\")[-1]}")
                        i += 1
                        continue

                elif file_name == self.ENDEKSVOLATILITE:

                    # Dosyanın tarih bilgisini alır.
                    date = self.file_dates[i]
                    XU030_path = self.indirme_dir + "\\" + self.UNZIPPED_VOLATILITE_030
                    XU100_path = self.indirme_dir + "\\" + self.UNZIPPED_VOLATILITE_100

                    # Dosyanın çıkarılma ismi kontrol edilir. 2. kontrol noktası.
                    if os.path.exists(self.indirme_dir + "\\" + self.UNZIPPED_VOLATILITE_030) or os.path.exists(self.indirme_dir + "\\" + self.UNZIPPED_VOLATILITE_030):
                        self.logger.debug(f"Dosya halihazırda bulunuyor. Dosya çıkarma işlemi yapılmıyor. Dosya adı: {self.file_name[i]}")
                        i += 1
                        continue

                    elif os.path.exists(XU030_path.split(".")[0] + "_" + date + self.CSV) or os.path.exists(XU100_path.split(".")[0] + "_" + date + self.CSV):
                        self.logger.debug(f"Dosya halihazırda bulunuyor. Dosya çıkarma işlemi yapılmıyor. Dosya adı: {self.file_names[i]}")
                        self.logger.debug(f"Dosya bilgileri alınıyor. Dosya adı: {XU030_path.split(".")[0] + "_" + date + self.CSV}")
                        path_list.append(XU030_path.split(".")[0] + "_" + date + self.CSV)
                        name_list.append(XU030_path.split(".")[0] + "_" + date)
                        self.logger.debug(f"Dosya bilgileri alınıyor. Dosya adı: {XU100_path.split(".")[0] + "_" + date + self.CSV}")
                        path_list.append(XU100_path.split(".")[0] + "_" + date + self.CSV)
                        name_list.append(XU100_path.split(".")[0] + "_" + date)
                        self.logger.debug("Dosya bilgileri alındı.")
                        i += 1
                        continue

                    # ZIP dosyası içindeki tüm dosyaları çıkarır.
                    self.logger.debug(f"Dosya çıkarma işlemi yapılıyor. Çıkarılan dosyanın adı: {self.file_names[i]}")
                    ZipFile(path).extractall(path = self.indirme_dir)
                    self.logger.debug(f"Dosya çıkarma işlemi yapıldı. Çıkarılan dosyanın adı: {self.file_names[i]}")

                    # Çıkarılan dosyaların bilgilerini alır.
                    self.logger.debug("Çıkarılan dosyaların yolu alınıyor...")
                    unzipped_file_paths = [XU030_path, XU100_path]
                    self.logger.debug("Çıkarılan dosyaların yolu alındı.")

                    # Çıkarılan dosyaların isimlerini, yollarını düzenler ve bir listeye ekler.
                    self.logger.debug("Çıkarılan dosyanın ismi düzenleniyor...")
                    for u_path in unzipped_file_paths:
                        new_name = u_path.split(".")[0] + "_" + date
                        new_path = u_path.split(".")[0] + "_" + date + self.CSV
                        self.__class__.unzipped_file_paths.append(new_path) # Dosyanın yeni yolunu listeye ekler.
                        self.__class__.unzipped_file_names.append(new_name) # Dosyanın yeni ismini listeye ekler.
                        os.rename(u_path, new_path)
                        self.logger.debug(f"Çıkarılan dosyanın ismi düzenlendi. Yeni dosya tam ismi: {new_name.split("\\")[-1]}")
                        
                else:
                    self.logger.debug("Geçersiz dosya ismi. Dosya çıkarma işlemi yapılmıyor.")
                    i += 1
                    continue

                i += 1
            self.logger.debug("Dosya çıkarma işlemi tamamlandı.")

            return path_list, name_list
        
        return unzip_files(file_name)
    
    # Dosyaları siler.
    def __delete_files(self) -> None:
        
        """
        Dosyaları siler.
        """
    
        @ErrorHandling.unexpected_error(self.logger, gmessage="Dosyalar silinemedi.", exit=True)
        def delete_files() -> None:
    
            if self.file_paths and self.unzipped_file_paths is []:
                self.logger.debug("Dosya bulunamadığı için işlem yapılmıyor.")
                self.logger.debug("Çıkış yapılıyor.")
                return None
            
            elif self.file_paths is not [] and self.unzipped_file_paths is []:
                for path in self.file_paths:
                    if os.path.exists(path):
                        os.remove(path)
                        self.logger.debug(f"Dosya silindi. Dosya ismi: {os.path.basename(path)}")
                    else:
                        self.logger.warning(f"Dosya bulunamadı. Dosya silinemedi. Dosya ismi: {os.path.basename(path)}")
    
                return None
            
            elif self.file_paths is [] and self.unzipped_file_paths is not []:                   
                for path in self.unzipped_file_paths:
                    if os.path.exists(path):
                        os.remove(path)
                        self.logger.debug(f"Dosya silindi. Dosya ismi: {os.path.basename(path)}")
                    else:
                        self.logger.warning(f"Dosya bulunamadı. Dosya silinemedi. Dosya ismi: {os.path.basename(path)}")
                        
                return None
            
            else:
                for path in self.file_paths:
                    if os.path.exists(path):
                        os.remove(path)
                        self.logger.debug(f"Dosya silindi. Dosya ismi: {os.path.basename(path)}")
                    else:
                        self.logger.warning(f"Dosya bulunamadı. Dosya silinemedi. Dosya ismi: {os.path.basename(path)}")
                        
                for path in self.unzipped_file_paths:
                    if os.path.exists(path):
                        os.remove(path)
                        self.logger.debug(f"Dosya silindi. Dosya ismi: {os.path.basename(path)}")
                    else:
                        self.logger.warning(f"Dosya bulunamadı. Dosya silinemedi. Dosya ismi: {os.path.basename(path)}")
                        
                return None
    
        return delete_files()
    
    # Değişkenleri sıfırlar.
    def __reset_variables(self) -> None:

        """
        Değişkenleri sıfırlar.
        """

        self.__class__.file_names = []
        self.__class__.file_paths = []
        self.__class__.table_names = []
        self.__class__.file_dates = []
        self.__class__.unzipped_file_paths = []
        self.__class__.unzipped_file_names = []
        self.logger.debug("Değişkenler sıfırlandı.")

        return None
    
    # PPGUNSONUFIYATHACIM dosyaları içindeki verileri DataFrame'e dönüştürür.
    def __ppgunsonufiyat(self) -> pd.DataFrame:

        """
        PPGUNSONUFIYATHACIM dosyaları içindeki Gün Sonu Fiyat Hacim verilerini DataFrame'e dönüştürür.
        """

        @ErrorHandling.unexpected_error(self.logger, gmessage= "PPGUNSONUFIYATHACIM dosyaları içindeki verileri DataFrame'e dönüştürme işlemi tamamlanamadı.", exit= True)
        def ppgunsonufiyat() -> pd.DataFrame:

            df_list = []
            k = 0

            if self.file_paths == None:
                self.logger.warning("Dosya ismi bulunamadığı için işlem yapılmıyor.")
                self.logger.debug("Çıkış yapılıyor.")
                return None

            # Dosya içindeki verileri DataFrame'e dönüştürür ve bir listeye ekler.
            for path in self.file_paths:
                
                self.logger.debug("Dosya DataFrame'e aktarılıyor. Dosya adı: " + self.file_names[k])
                df = pd.read_csv(path, header=None, names=ColumnNames.fiyathacim , delimiter=";", dtype=Dtypes.fiyathacim, skiprows=2)
                self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + self.file_names[k])

                self.logger.debug("İstenmeyen tablolar düşürülüyor...")
                df = df[df["BIST_100_INDEX"] == 1]
                df = df.drop(labels=Deletables.fiyathacim, axis=1)
                self.logger.debug("İstenmeyen tablolar düşürüldü.")

                self.logger.debug("Biçimlendirme yapılıyor...")
                df["DATE"] = df["DATE"].str.replace(".","-")
                df["STOCK_CODE"] = df["STOCK_CODE"].str.split(".", expand=True)[0]
                self.logger.debug("Biçimlendirme yapıldı.")

                self.logger.debug("Tarihi ve alfabetik sıralama yapılıyor...")
                df = df.sort_values(by=["STOCK_CODE", "DATE"], ascending=True)
                self.logger.debug("Tarihi ve alfabetik sıralama yapıldı.")

                self.logger.debug("NaN değerler dolduruluyor...")
                df = df.fillna(0)
                self.logger.debug("NaN değerler dolduruldu.")

                self.logger.debug("DataFrame listesine ekleme yapılıyor...")
                df_list.append(df)
                self.logger.debug("DataFrame listesine ekleme yapıldı.")

                self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + self.file_names[k])
                k += 1

            # DataFrame'leri tek bir DataFrame'de birleştirir.
            self.logger.debug("DataFrame'ler birleştiriliyor...")
            df = pd.concat(df_list, ignore_index = True)
            self.logger.debug("Tüm DataFrame'ler birleştirildi.")

            return df

        return ppgunsonufiyat()
        
    # PPGUNSONUENDEKSHACIM dosyaları içindeki verileri DataFrame'e dönüştürür.
    def __ppgunsonuendeks(self) -> pd.DataFrame:

        """
        PPGUNSONUENDEKSHACIM dosyaları içindeki Gün Sonu Endeks Hacim verilerini DataFrame'e dönüştürür.
        """

        @ErrorHandling.unexpected_error(self.logger, gmessage= "PPGUNSONUENDEKSHACIM dosyaları içindeki verileri DataFrame'e dönüştürme işlemi tamamlanamadı.", exit= True)
        def ppgunsonuendeks() -> pd.DataFrame:

            df_list = []
            k = 0

            if self.file_paths == None:
                self.logger.debug("Dosya ismi bulunamadığı için işlem yapılmıyor.")
                self.logger.debug("Çıkış yapılıyor.")
                return None

            # ZIP dosyası içindeki istenen dosyayı çıkarır ve ismini düzenler.
            unzipped_file_info = self.__unzip_files(self.ENDEKSHACIM, self.CSV)
            path_list = unzipped_file_info[0]

            # Çıkarılan dosya içindeki verileri DataFrame'e dönüştürür ve bir listeye ekler.
            for path in self.unzipped_file_paths:

                if path == os.path.join(self.indirme_dir, self.UNZIPPED_ENDEKSHACIM):
                    self.logger.debug(f"İstenmeyen dosya olduğu için DataFrame'e aktarma işlemi yapılmıyor. Dosya adı: {os.path.basename(path)}")
                    continue

                self.logger.debug(f"Dosya DataFrame'e aktarılıyor. Dosya adı: {os.path.basename(path)}")
                df = pd.read_csv(path, header=None, names=ColumnNames.endekshacim , delimiter=";", dtype=Dtypes.endekshacim, encoding="utf-16", skiprows=3)
                self.logger.debug(f"Dosya DataFrame'e aktarıldı. Dosya adı: {os.path.basename(path)}")

                df = df[df["INDEX_TYPE"] == "Fiyat"]
                df = df[df["INDEX_NAMES_IN_ENGLISH"].str.contains("CAPPED") == False]
                df = df[df["INDEX_NAMES_IN_ENGLISH"].str.contains("EQUAL") == False]
                df = df.drop(labels=Deletables.endekshacim, axis=1)
                self.logger.debug("İstenmeyen satırlar ve sütunlar düşürüldü.")

                df["DATE"] = df["DATE"].str.replace("/","-")
                df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%m-%Y").dt.strftime('%Y-%m-%d')
                self.logger.debug("Tarih biçimlendirmesi yapıldı.")

                df = df.sort_values(by=["INDEX_CODE", "DATE"], ascending=True)
                self.logger.debug("Tarihi ve alfabetik sıralama yapıldı.")

                df = df.fillna(0)
                self.logger.debug("NaN değerleri 0 ile değiştirildi.")

                df_list.append(df)
                self.logger.debug("DataFrame listesine ekleme yapıldı.")

                self.logger.debug(f"Dosya DataFrame'e aktarıldı. Dosya adı: {os.path.basename(path)}")
                k += 1

            # Çıkarılan dosyaları siler.
            self.logger.debug("Çıkarılan dosyalar siliniyor...")
            self.__delete_files(self.unzipped_file_paths)
            self.logger.debug("Çıkarılan dosyalar silindi.")

            # DataFrame'leri tek bir DataFrame'de birleştirir.
            self.logger.debug("DataFrame'ler birleştiriliyor...")
            df = pd.concat(df_list, ignore_index = True)
            self.logger.debug("Tüm DataFrame'ler birleştirildi.")

            return df

        return ppgunsonuendeks()
    
    # hisse_endeks_ds dosyaları içindeki verileri DataFrame'e dönüştürür.
    def __cariendekshisse(self, files_dict: dict) -> pd.DataFrame:

        """
        hisse_endeks_ds dosyaları içindeki cari endeks-hisse verilerini DataFrame'e dönüştürür.
        """

        @ErrorHandling.unexpected_error(self.logger, gmessage= "hisse_endeks_ds dosyaları içindeki verileri DataFrame'e dönüştürme işlemi tamamlanamadı.", exit= True)
        def hisseendekshisse(files_dict: dict) -> pd.DataFrame:

            df_list = []
            k = 0

            if files_dict == None:
                self.logger.debug("Dosya ismi bulunamadığı için işlem yapılmıyor.")
                self.logger.debug("Çıkış yapılıyor.")
                return None

            # Dosya içindeki verileri DataFrame'e dönüştürür ve bir listeye ekler.
            for path in files_dict["file_path"]:
                self.logger.debug("Dosya DataFrame'e aktarılıyor. Dosya adı: " + files_dict["file_name"][k])
                df = pd.read_csv(path, header=None, names=ColumnNames.cariendekshisse , delimiter=";", dtype=Dtypes.cariendekshisse, skiprows=2)
                self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + files_dict["file_name"][k])

                self.logger.debug("Tarih ve alfabetik sıralama yapılıyor...")
                df = df.sort_values(by=["STOCK_CODE", "INDEX_CODE"], ascending=True)
                self.logger.debug("Tarih ve alfabetik sıralama yapıldı.")

                self.logger.debug("Veri biçimlendirme yapılıyor...")
                df["DATE"] = df["DATE"].str.replace("/","-")
                df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%m-%Y").dt.strftime('%Y-%m-%d')
                df["STOCK_CODE"] = df["STOCK_CODE"].str.split(".", expand=True)[0]
                self.logger.debug("Veri biçimlendirme yapıldı.")

                self.logger.debug("NaN değerler dolduruluyor...")
                df = df.fillna(0)
                self.logger.debug("NaN değerler dolduruldu.")

                self.logger.debug("DataFrame listesine ekleme yapılıyor...")
                df_list.append(df)
                self.logger.debug("DataFrame listesine ekleme yapıldı.")

                self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + files_dict["file_name"][k])
                k += 1

            # DataFrame'leri tek bir DataFrame'de birleştirir.
            self.logger.debug("DataFrame'ler birleştiriliyor...")
            df = pd.concat(df_list, ignore_index = True)
            self.logger.debug("Tüm DataFrame'ler birleştirildi.")

            return df

        return hisseendekshisse(files_dict)
        
    # exsrk dosyaları içindeki verileri DataFrame'e dönüştürür.
    def __eskiendekshisse(self, files_dict: dict) -> pd.DataFrame:

        """
        exsrk dosyaları içindeki geçmiş senelere ait endeks-hisse verilerini DataFrame'e dönüştürür.
        """

        @ErrorHandling.unexpected_error(self.logger, gmessage= "exsrk dosyaları içindeki verileri DataFrame'e dönüştürme işlemi tamamlanamadı.", exit= True)
        def eskiendekshisse(files_dict: dict) -> pd.DataFrame:

            df_list = []
            k = 0

            if files_dict == None:
                self.logger.debug("Dosya ismi bulunamadığı için işlem yapılmıyor.")
                self.logger.debug("Çıkış yapılıyor.")
                return None

            # ZIP dosyası içindeki istenen dosyayı çıkarır ve ismini düzenler.

            unzipped_file_info = self.__unzip_files(self.ESKIENDEKS, files_dict, self.XLSX)[0] # Çıkarılan dosyanın bilgilerini dict olarak alır. ???????XLSX???????

            # Çıkarılan dosya içindeki verileri DataFrame'e dönüştürür ve bir listeye ekler.

            for path in unzipped_file_info["file_path"]:

                year = unzipped_file_info["file_date"][k] # Yıl bilgisini alır.

                if int(year) >= 2022:
                    column = ColumnNames.eskiendekshisse
                    dtype = Dtypes.eskiendekshisse
                    deletables = Deletables.eskiendekshisse
                    aranan_kod = "ZRGYO"
                else:
                    column = ColumnNames.eskiendekshisse_V2
                    dtype = Dtypes.eskiendekshisse_V2
                    deletables = Deletables.eskiendekshisse_V2
                    aranan_kod = "YONGA"
                
                self.logger.debug("Dosya DataFrame'e aktarılıyor. Dosya adı: " + unzipped_file_info["file_name"][k].split("\\")[-1])
                df = pd.read_excel(path, header=None, names=column , dtype=dtype, skiprows=4)
                self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + unzipped_file_info["file_name"][k].split("\\")[-1])

                self.logger.debug("İstenmeyen tablolar düşürülüyor...")
                df = df.drop(labels=deletables, axis=1)
                self.logger.debug("İstenmeyen tablolar düşürüldü.")

                rows = len(df.axes[0]) # Satır sayısını alır.
                year_column = [] # Yıl sütununu eklemek için bir liste oluşturur.

                # Yıl listesini oluşturur.
                self.logger.debug("Yıl sütunu oluşturuluyor...")
                for row in range(0,rows):
                    year_column.append(year)
                self.logger.debug("Yıl sütunu oluşturuldu.")

                # Yıl sütununu DataFrame'e ekler.
                self.logger.debug("Yıl sütunu ekleniyor...")
                df.insert(0, "DATE", year_column, True)
                self.logger.debug("Yıl sütunu eklendi.")

                # Pazarı kapanan hisselerin kodunu düşürür.
                final_index = df.index[df["STOCK_CODE"] == aranan_kod].to_list() # Aranan hisse kodunun indexini alır.
                df.drop(df.index[final_index[0]:(rows)], inplace=True) # Aranan hisse kodunu düşürür.

                # Tarihi ve alfabetik sıralama yapar.
                self.logger.debug("Tarihi ve alfabetik sıralama yapılıyor...")
                df = df.sort_values(by=["STOCK_CODE", "DATE"], ascending=True) #?????
                self.logger.debug("Tarihi ve alfabetik sıralama yapıldı.")

                # NaN değerleri doldurur.
                self.logger.debug("NaN değerler dolduruluyor...")
                df = df.fillna("-")
                self.logger.debug("NaN değerler dolduruldu.")

                # DataFrame listesine ekler.
                self.logger.debug("DataFrame listesine ekleme yapılıyor...")
                df_list.append(df)
                self.logger.debug("DataFrame listesine ekleme yapıldı.")

                self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + unzipped_file_info["file_name"][k].split("\\")[-1])
                k += 1

            # Çıkarılan dosyaları siler.
            self.logger.debug("Çıkarılan dosyalar siliniyor...")
            self.__delete_files(unzipped_file_info["file_path"])
            self.logger.debug("Çıkarılan dosyalar silindi.")

            # DataFrame'leri tek bir DataFrame'de birleştirir.
            self.logger.debug("DataFrame'ler birleştiriliyor...")
            df = pd.concat(df_list, ignore_index = True)
            self.logger.debug("Tüm DataFrame'ler birleştirildi.")

            return df

        return eskiendekshisse(files_dict)
    
    # volatilite dosyaları içindeki verileri DataFrame'e dönüştürür.
    def __endeksvolatilite(self, files_dict: dict) -> pd.DataFrame:

        """
        Volatilite dosyaları içindeki endeks volatilite verilerini DataFrame'e dönüştürür.
        """

        @ErrorHandling.unexpected_error(self.logger, gmessage= "Volatilite dosyaları içindeki verileri DataFrame'e dönüştürme işlemi tamamlanamadı.", exit= True)
        def endeksvolatilite(files_dict: dict) -> pd.DataFrame:

            if files_dict == None:
                self.logger.debug("Dosya ismi bulunamadığı için işlem yapılmıyor.")
                self.logger.debug("Çıkış yapılıyor.")
                return None

            engine = create_engine(conn_string(DatabaseNames.finansal)) # Veritabanı bağlantısı oluşturur.
            metadata = MetaData()
            df_list_030 = []
            df_list_100 = []
            len_30 = 0
            len_100 = 0

            row_count_list = HistoricalDataModul(engine, metadata).get_row_length(DatabaseTables.datastore_h_volatility) # Veritabanındaki tablonun satır sayısını alır.
            row_count_030 = row_count_list[0]
            row_count_100 = row_count_list[1]
            
            if row_count_030 == 0:
                row_count_030 = 1
            if row_count_100 == 0:
                row_count_100 = 1

            k = 0
            j = 0

            # ZIP dosyası içindeki istenen dosyayı çıkarır ve ismini düzenler.

            unzipped_file_info = self.__unzip_files(self.ENDEKSVOLATILITE, files_dict, self.CSV)
            path_list = unzipped_file_info[0]
            name_list = unzipped_file_info[1]

            # Çıkarılan dosya içindeki verileri DataFrame'e dönüştürür ve bir listeye ekler.

            for path in path_list:

                if self.UNZIPPED_VOLATILITE_030.split(".")[0] in path:
                    self.logger.debug("Dosya DataFrame'e aktarılıyor. Dosya adı: " + name_list[k+j].split("\\")[-1])
                    df = pd.read_csv(path, header=None, names=ColumnNames.endeksvolatilite , delimiter=";", dtype=Dtypes.endeksvolatilite, encoding="utf-16", skiprows=3)
                    self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + name_list[k+j].split("\\")[-1])

                    # İstenmeyen tabloları düşürür.
                    self.logger.debug("İstenmeyen tablolar düşürülüyor...")
                    df = df.drop(labels=Deletables.endeksvolatilite, axis=1)
                    self.logger.debug("İstenmeyen tablolar düşürüldü.")

                    # Tarih biçimlendirmesi yapar.
                    self.logger.debug("Tarih biçimlendirmesi yapılıyor...")
                    df["DATE"] = df["DATE"].str.replace(".","-")
                    df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%m-%Y").dt.strftime('%Y-%m-%d')
                    self.logger.debug("Tarih biçimlendirmesi yapıldı.")

                    # NaN değerleri doldurur.
                    self.logger.debug("NaN değerler dolduruluyor...")
                    df = df.fillna(0)
                    self.logger.debug("NaN değerler dolduruldu.")

                    # DataFrame'leri artan sıraya göre sıralar.
                    self.logger.debug("DataFrame artan sıraya göre sıralanıyor...")
                    df = df.sort_values(by=["DATE", "NUMBER_OF_DAYS"], ascending=True)
                    self.logger.debug("DataFrame artan sıraya göre sıralandı.")

                    # DataFrame listesine ekler.
                    self.logger.debug("DataFrame listesine ekleme yapılıyor...")
                    if len(df.axes[0]) > row_count_030:

                        # İlk DataFrame'i karşılaştırabilmek için veri tabanındaki tablonun son satır sayısı kullanılır.
                        if k == 0:
                            if row_count_030 == 1:
                                df_list_030.append(df[(row_count_030 - 1):])
                                len_30 = len(df.axes[0])
                            else:
                                df_list_030.append(df[(row_count_030):])
                                len_30 = len(df.axes[0])

                        # Bir önceki DataFrame'in son satır sayısı kullanılır.
                        elif k > 0:
                            if row_count_030 == 1:
                                df = df[(row_count_030 + len_30 - 1):]
                                df_list_030.append(df)
                                len_30 = len(df.axes[0]) + len_30
                            else:
                                df = df[(len_30):]
                                df_list_030.append(df)
                                len_30 = len(df.axes[0]) + len_30

                        self.logger.debug("DataFrame listesine ekleme yapıldı.")

                    # DataFrame'in satır sayısı veri tabanındaki tablonun son satır sayısından küçükse DataFrame veri tabanına eklenir.
                    elif len(df.axes[0]) <= row_count_030:
                        self.logger.debug("Veri halihazırda işlenmiş. DataFrame listesine ekleme yapılmıyor. Dosya adı: " + name_list[k+j].split("\\")[-1])

                    self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + name_list[k+j].split("\\")[-1])
                    k += 1

                elif self.UNZIPPED_VOLATILITE_100.split(".")[0] in path:

                    # Dosya içindeki verileri DataFrame'e dönüştürür.
                    self.logger.debug("Dosya DataFrame'e aktarılıyor. Dosya adı: " + name_list[k+j].split("\\")[-1])
                    df = pd.read_csv(path, header=None, names=ColumnNames.endeksvolatilite , delimiter=";", dtype=Dtypes.endeksvolatilite, encoding="utf-16", skiprows=3)
                    self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + name_list[k+j].split("\\")[-1])

                    # İstenmeyen sütunları düşürür.
                    self.logger.debug("İstenmeyen sütunlar düşürülüyor...")
                    df = df.drop(labels=Deletables.endeksvolatilite, axis=1)
                    self.logger.debug("İstenmeyen sütunlar düşürüldü.")

                    # Tarih biçimlendirmesi yapar.
                    self.logger.debug("Tarih biçimlendirmesi yapılıyor...")
                    df["DATE"] = df["DATE"].str.replace(".","-")
                    df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%m-%Y").dt.strftime('%Y-%m-%d')
                    self.logger.debug("Tarih biçimlendirmesi yapıldı.")

                    # NaN değerleri doldurur.
                    self.logger.debug("NaN değerler dolduruluyor...")
                    df = df.fillna(0)
                    self.logger.debug("NaN değerler dolduruldu.")

                    # DataFrame'leri artan sıraya göre sıralar.
                    self.logger.debug("DataFrame artan sıraya göre sıralanıyor...")
                    df = df.sort_values(by=["DATE", "NUMBER_OF_DAYS"], ascending=True)
                    self.logger.debug("DataFrame artan sıraya göre sıralandı.")

                    # DataFrame listesine ekler.
                    self.logger.debug("DataFrame listesine ekleme yapılıyor...")
                    if len(df.axes[0]) > row_count_100:

                        # İlk DataFrame'i karşılaştırabilmek için veri tabanındaki tablonun son satır sayısı kullanılır.
                        if j == 0:
                            if row_count_100 == 1:
                                df_list_100.append(df[(row_count_100 - 1):])
                                len_100 = len(df.axes[0])
                            else:
                                df_list_100.append(df[(row_count_100):])
                                len_100 = len(df.axes[0])

                        # Bir önceki DataFrame'in son satır sayısı kullanılır.
                        elif j > 0:
                            if row_count_100 == 1:
                                df = df[(row_count_100 + len_100 - 1):]
                                df_list_100.append(df)
                                len_100 = len(df.axes[0]) + len_100
                            else:
                                df = df[(len_100):]
                                df_list_100.append(df)
                                len_100 = len(df.axes[0]) + len_100

                        self.logger.debug("DataFrame listesine ekleme yapıldı.")

                    # Eğer DataFrame'in satır sayısı veri tabanındaki tablodan küçükse DataFrame listesine eklenmez.
                    elif len(df.axes[0]) <= row_count_100:
                        self.logger.debug("Veri halihazırda işlenmiş. DataFrame listesine ekleme yapılmıyor. Dosya adı: " + name_list[j+k].split("\\")[-1])

                    self.logger.debug("Dosya DataFrame'e aktarıldı. Dosya adı: " + name_list[j+k].split("\\")[-1])
                    j += 1

            # Çıkarılan dosyaları siler.
            self.logger.debug("Çıkarılan dosyalar siliniyor...")
            self.__delete_files(path_list)
            self.logger.debug("Çıkarılan dosyalar silindi.")

            # DataFrame'leri tek bir DataFrame'de birleştirir.
            self.logger.debug("DataFrame'ler birleştiriliyor...")
            try:
                df_030 = pd.concat(df_list_030, ignore_index = True)
                df_100 = pd.concat(df_list_100, ignore_index = True)
                df = pd.concat([df_030, df_100], ignore_index = True)
                df = df.sort_values(by=["DATE", "NUMBER_OF_DAYS", "INDEX_CODE"], ascending=True)
            except ValueError:
                self.logger.warning("DataFrame'ler birleştirilirken bir hata oluştu. Birleştirilecek DataFrame bulunamadı.")
                return None
            except:
                self.logger.warning("DataFrame'ler birleştirilirken beklenmeyen bir hata oluştu.")
                return None

            self.logger.debug("Tüm DataFrame'ler birleştirildi.")
            return df

        return endeksvolatilite(files_dict)
        
    @staticmethod
    def __formalization(vb_obj, logger: logging.Logger, file_name: str) -> pd.DataFrame:

        """
        Dosya içindeki verileri DataFrame'e dönüştürür.
        """

        @ErrorHandling.unexpected_error(logger, gmessage= f"{file_name} dosyaları içindeki verileri DataFrame'e dönüştürme işlemi tamamlanamadı.", exit= True)
        def formalization(vb_obj, logger: logging.Logger, file_name: str) -> pd.DataFrame:
            logger = logger
            logger.debug("Veri Biçimlendirme işlemi başlatılıyor.")

            logger.debug("Veri Biçimlendirme nesnesi oluşturuluyor.")
            veri_bicimlendirme = vb_obj(logger)
            logger.debug("Veri Biçimlendirme nesnesi oluşturuldu.")

            # Dosyanın var olup olmadığını kontrol eder.
            if file_name == None:
                logger.debug("Dosya ismi bulunamadığı için işlem yapılmıyor.")
                logger.debug("Çıkış yapılıyor.")
                return None
            
            else:
                logger.debug("Dosya verilerini elde etme metodu çağrılıyor.")
                veri_bicimlendirme.__get_file_info(file_name)
                logger.debug("Dosya verilerini elde etme metodu çağrıldı.")
                
            file_name_list = DSFileNames.get_file_name_list()
            
            # Dosya içindeki verileri DataFrame'e dönüştürür. !!!HATA VAR!!!
            if file_name in file_name_list:
                logger.debug(f"{file_name} dosyaları içindeki veriler DataFrame'e dönüştürme işlemi başlatılıyor.")
                df = veri_bicimlendirme.__ppgunsonufiyat()
                logger.debug(f"{file_name} dosyaları içindeki veriler DataFrame'e dönüştürme işlemi tamamlandı.")
            
            else:
                logger.debug(f"{file_name} dosyaları herhangi bir kayda denk gelmiyor.")
                logger.debug("Çıkış yapılıyor.")
                return None
            
            logger.debug("Tabloya eklenen dosyalar siliniyor.")
            veri_bicimlendirme.__delete_files(files_dict)
            logger.debug("Tabloya eklenen dosyalar silindi.")
            
            veri_bicimlendirme.__reset_variables()
            
            logger.debug("Veri Biçimlendirme işlemi tamamlandı.")
            return df
        
        return formalization(vb_obj, logger, file_name)

    # Veri Biçimlendirme modülü
    @staticmethod
    def VM_TV_VB() -> list:
        
        """
        Tarihsel veri biçimlendirme modülü.
        """

        logger = LoggerObjects.VM_TV_VB_logger

        @ErrorHandling.unexpected_error(logger, gmessage= "Tarihsel veri biçimlendirme modülü tamamlanamadı.", exit= True)
        def VM_TV_VB(logger) -> list:

            vb_obj = DSFormalization

            logger.info("Tarihsel Veri Biçimlendirme modülü başlatıldı.")

            df_gsf = DSFormalization.__formalization(vb_obj, LoggerObjects.GSF_logger, DSFileNames.FIYATHACIM) # Gün Sonu Fiyat

            df_gse = DSFormalization.__formalization(vb_obj, LoggerObjects.GSE_logger, DSFileNames.ENDEKSHACIM) # Gün Sonu Endeks

            df_eeh = DSFormalization.__formalization(vb_obj, LoggerObjects.EEH_logger, DSFileNames.ESKIENDEKS) # Eski Endeks Hisse

            if df_gsf is None and df_gse is None and df_eeh is None:
                logger.warning("Veri Biçimlendirme modülü çalıştırıldı ancak herhangi bir veri bulunamadı.")
                logger.warning("Uygulama sonlandırılıyor.")
                sys.exit()

            df_list = [df_gsf, df_gse, df_eeh]

            logger.info("Veri Biçimlendirme modülü tamamlandı.")

            return df_list

        return VM_TV_VB(logger)

    # Veri Biçimlendirme modülü
    @staticmethod
    def VM_EVG_VB() -> list:

        """
        Endeks veri biçimlendirme modülü.
        """

        logger = LoggerObjects.VM_EVG_VB_logger # VM_EVG_VB: Veri Modülü - Yardımcı Modüller - Endeks Verileri Güncelleme - Veri Biçimlendirme

        @ErrorHandling.unexpected_error(logger, gmessage= "Endeks veri biçimlendirme modülü tamamlanamadı.", exit= True)
        def VM_EVG_VB(logger) -> list:

            vb_obj = DSFormalization

            logger.info("Veri Biçimlendirme modülü başlatıldı.")

            df_ceh = DSFormalization.__formalization(vb_obj, LoggerObjects.CEH_logger, DSFileNames.CARIENDEKS) # Cari Endeks Hisse

            df_ev = DSFormalization.__formalization(vb_obj, LoggerObjects.EV_logger, DSFileNames.ENDEKSVOLATILITE) # Endeks Volatilite

            if df_ceh is None and df_ev is None:
                logger.warning("Veri Biçimlendirme modülü çalıştırıldı ancak herhangi bir veri bulunamadı.")
                logger.warning("Uygulama sonlandırılıyor.")
                sys.exit()

            df_list = [df_ceh, df_ev]

            logger.info("Veri Biçimlendirme modülü tamamlandı.")

            return df_list
        
        return VM_EVG_VB(logger)
