import deneme1
import deneme2

# Güncelleme işlemi
updater = deneme1.UpdateIndexData()
updater.update_data()

# module1'de güncellenen veriler module2'de okunabilir
reader = deneme2.ReadIndexData()
reader.read_data()
