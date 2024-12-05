import sys
from logging import Logger as _Logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotVisibleException, ElementClickInterceptedException, UnexpectedTagNameException
from selenium.common.exceptions import WebDriverException, JavascriptException, NoSuchWindowException, ElementNotInteractableException
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError, IntegrityError, DataError, InterfaceError, InvalidRequestError, NoResultFound, MultipleResultsFound
from sqlalchemy.exc import NoSuchTableError, NoSuchColumnError
from threading import ThreadError
from queue import Empty, Full

import requests

def conn_control():

    """
    İnternet bağlantı kontrolü yapar.
    """

    url = "http://www.google.com"
    timeout = 5
    
    try:
        response = requests.get(url, timeout=timeout)
        return True
    
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False
    
class ErrorHandling:

    """
    ErrorHandling sınıfı, hata durumlarında uygulamanın gerekli davranışı sergilemesini sağlayan decorator fonksiyonları içerir.
    """

    @staticmethod
    def unexpected_error(logger: _Logger, gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True, error_value: bool = False):

        """
        Beklenmeyen hata durumunda uygulamanın sonlandırılmasını sağlar. Genel hatadır, tüm hata türlerini yakalar. Her zaman tercih edilmemelidir.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()
                    if error_value:
                        return True
                    
            return wrapper
        
        return decorator

    @staticmethod
    def stopiteration_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        StopIteration hatası durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except StopIteration as e:
                    logger.critical(f"İterasyon sonu. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

class SeleniumErrorHandling:
    
    """
    SeleniumErrorHandling sınıfı, Selenium kütüphanesini kullanırken karşılaşılabilecek hatalara ilişkin
    decorator fonksiyonlarını içerir.
    """
    
    @staticmethod
    def webdriver_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Genel Selenium hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except WebDriverException as e:
                    logger.critical(f"WebDriver hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def nosuchelement_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Element bulunamadığında uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except NoSuchElementException as e:
                    logger.critical(f"Element bulunamadı. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

    @staticmethod
    def timeout_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True, error_value: bool = False, repeat: bool = False):

        """
        Zaman aşımı durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except TimeoutException as e:
                    logger.critical(f"Zaman aşımı. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()
                    if error_value:
                        return False
                    if repeat:
                        logger.debug("İşlem tekrar deneniyor.")
                    
                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

    @staticmethod
    def elementnotvisible_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Element görünür olmadığında uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except ElementNotVisibleException as e:
                    logger.critical(f"Element görünür değil. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

    @staticmethod
    def elementclickintercepted_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Elemente tıklanamadığında uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):
                
                try:
                    return func(*args, **kwargs)
                
                except ElementClickInterceptedException as e:
                    logger.critical(f"Elemente tıklanamadı. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

    @staticmethod
    def unexpectedtagname_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Select elementi bulunamadığında uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except UnexpectedTagNameException as e:
                    logger.critical(f"Select elementi bulunamadı. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

    @staticmethod
    def javascript_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Javascript hatalarında uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except JavascriptException as e:
                    logger.critical(f"Javascript hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def window_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Window hatalarında uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except NoSuchWindowException as e:
                    logger.critical(f"Window hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def elementnotinteractable_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = False):

        """
        Elemente tıklanamadığında uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):
                
                try:
                    return func(*args, **kwargs)
                
                except ElementNotInteractableException as e:
                    logger.critical(f"Elemente tıklanamadı. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

    @staticmethod
    def attribute_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = False):

        """
        Attribute hatası durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):
                
                try:
                    return func(*args, **kwargs)
                
                except AttributeError as e:
                    logger.critical(f"Attribute hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()
                        
                except WebDriverException as e:
                    logger.critical(f"Webdriver'da beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator

class ThreadErrorHandling:
    
    """
    ThreadErrorHandling sınıfı, çoklu iş parçacığı kullanımında karşılaşılabilecek hatalara ilişkin
    decorator fonksiyonlarını içerir.
    """

    @staticmethod
    def thread_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = False):

        """
        Genel thread hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):
                
                try:
                    return func(*args, **kwargs)
                
                except ThreadError as e:
                    logger.critical(f"Thread hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()
                
                except Exception as e:
                    logger.critical(f"Thread hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

            return wrapper
        
        return decorator

    @staticmethod
    def queue_empty_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", error_value: bool = False, exit: bool = False):

        """
        Queue boş olduğunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):
                
                try:
                    return func(*args, **kwargs)
                
                except Empty as e:
                    logger.critical(f"Queue boş. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()
                    if error_value:
                        return True

            return wrapper
        
        return decorator
    
    @staticmethod
    def queue_full_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", error_value: bool = False, exit: bool = False):

        """
        Queue dolu olduğunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):
                
                try:
                    return func(*args, **kwargs)
                
                except Full as e:
                    logger.critical(f"Queue dolu. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()
                    if error_value:
                        return True

            return wrapper
        
        return decorator

class SQLAlchemyErrorHandling:
    
    """
    SQLAlchemyErrorHandling sınıfı, SQLAlchemy kütüphanesini kullanırken karşılaşılabilecek hatalara ilişkin
    decorator fonksiyonlarını içerir.
    """

    @staticmethod
    def sqlalchemy_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        SQLAlchemy hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except SQLAlchemyError as e:
                    logger.critical(f"SQLAlchemy hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()
                    
            return wrapper
        
        return decorator

    @staticmethod
    def operational_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Operational hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except OperationalError as e:
                    logger.critical(f"Operational hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
  
    @staticmethod
    def integrity_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Integrity hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except IntegrityError as e:
                    logger.critical(f"Integrity hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
   
    @staticmethod
    def data_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Data hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except DataError as e:
                    logger.critical(f"Data hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def programming_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Programming hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except ProgrammingError as e:
                    logger.critical(f"Programming hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
       
    @staticmethod
    def interface_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Interface hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except InterfaceError as e:
                    logger.critical(f"Interface hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def invalidrequest_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Invalid request hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except InvalidRequestError as e:
                    logger.critical(f"Invalid request hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def noresultfound_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        No result found hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except NoResultFound as e:
                    logger.critical(f"No result found hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def multipleresultsfound_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        Multiple results found hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except MultipleResultsFound as e:
                    logger.critical(f"Multiple results found hatası. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    
    @staticmethod
    def nosuchtable_error(logger: _Logger, emessage: str = "Uygulama sonlandırılıyor.", gmessage: str = "Uygulama sonlandırılıyor.", exit: bool = True):

        """
        No such table hataları için kullanılan decorator. Hata durumunda uygulamanın sonlandırılmasını sağlar.
        """

        def decorator(func: callable):

            def wrapper(*args, **kwargs):

                try:
                    return func(*args, **kwargs)
                
                except NoSuchTableError as e:
                    logger.critical(f"Belirtilen tablo bulunamadı. {emessage}")
                    logger.debug(f"{e}")
                    if exit:
                        logger.critical("Uygulama sonlandırılıyor.")
                        sys.exit()

                except SQLAlchemyError as e:
                    logger.critical(f"Beklenmeyen bir SQLAlchemy hatası oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()
                    
                except Exception as e:
                    logger.critical(f"Beklenmeyen bir hata oluştu. {gmessage}")
                    logger.debug(f"{e}")
                    logger.critical("Uygulama sonlandırılıyor.")
                    sys.exit()

            return wrapper
        
        return decorator
    