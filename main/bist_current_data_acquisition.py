import sys
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python\auxiliary") # Yardımcı Modül dosyalarının bulunduğu dizin eklenir.
sys.path.append(r"C:\Users\furka\OneDrive\Belgeler\Proje X\Python")

from acquisition.financialdata.current_data_acquisition import ft_live_data, conn_control
from database.acquisition.current_database import ft_data_to_database

from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor

def main() -> None:

    #######################################################################################################################
    # İş Parçacığı Yöneticisi ile iş parçacıklarının eş zamanlı çalıştırılması sağlanır.
    # ft_live_data ve ft_data_to_database fonksiyonları eş zamanlı olarak çalıştırılır.
    # ft_live_data fonksiyonu ile finansal veriler alınırken, ft_data_to_database fonksiyonu ile veritabanına kaydedilir.
    # Tasarım ilerleyen aşamalarda yapılacak testler ve geri bildirimler doğrultusunda geliştirilecektir.
    # Farklı iş parçacıkları yerine farklı işlemler olarak da tasarlanabilir.
    #######################################################################################################################

    with _ThreadPoolExecutor() as executor:
        
        executor.submit(conn_control)
        executor.submit(ft_live_data)
        executor.submit(ft_data_to_database)
        
    return None

main()