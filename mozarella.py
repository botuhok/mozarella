#!/usr/bin/python3.11
# TODO: блокировка рекламы 
# URL_adblock = "https://easylist.to/easylist/easylist.txt"
help_text = r"""

█▄─▀█▀─▄██─▄▄─██░▄▄░▄███▀▄─███▄─▄▄▀██▄─▄▄─██▄─▄████▄─▄█████▀▄─██
██─█▄█─███─██─███▀▄█▀███─▀─████─▄─▄███─▄█▀███─██▀███─██▀███─▀─██
▀▄▄▄▀▄▄▄▀▀▄▄▄▄▀▀▄▄▄▄▄▀▀▄▄▀▄▄▀▀▄▄▀▄▄▀▀▄▄▄▄▄▀▀▄▄▄▄▄▀▀▄▄▄▄▄▀▀▄▄▀▄▄▀
                           BROWSER

                          ∙∙∙∙∙·▫▫ᵒᴼᵒ▫ₒₒ▫ᵒᴼᵒ▫ₒₒ▫ᵒᴼᵒ☼)===> About:

This is a test browser created for my own needs. 
It can:
  ● work with tabs;
  ● block ads from easylist, which is downloaded automatically;
  ● disable javascript from pages;
  ● disable images from pages;
  ● use tor for loading pages;

It can't:
  ● store your passwords
  ● remember your history
  ● add pages to favorites
         ... and much more
  
                    ∙∙∙∙∙·▫▫ᵒᴼᵒ▫ₒₒ▫ᵒᴼᵒ▫ₒₒ▫ᵒᴼᵒ☼)===> For use tor:

  ● download fresh tor from https://www.torproject.org/download/
  ● put all tor files in mozarella\tor folder and create torrc.
       example:
            SOCKSPort 9052
            GeoIPFile geoip
            GeoIPv6File geoip6
            CookieAuthentication 1

  ● run browser from command line:
            python mozarella.py -tor
                    or 
            mozarella.exe -tor

"""

from adblockparser import AdblockRules
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import QNetworkProxy
# from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage, QWebEngineProfile as QWebProfile
from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
from PyQt5 import QtWebEngineCore, QtWebEngineWidgets
from PyQt5.QtPrintSupport import *

import re
import sys


# for download files
import requests
import shutil



# debug info
# os.environ['QT_DEBUG_PLUGINS']='1'
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu-command-logging"
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"]="--disable-gpu"               # отключение рендеринга через видяху


##### загружаем пустые правила 
with open("nothing.txt") as f:
    raw_rules = f.readlines()
    rules = AdblockRules(raw_rules)

class WebEngineUrlRequestInterceptor(QtWebEngineCore.QWebEngineUrlRequestInterceptor):
    """ класс для обработки блокировки рекламы """
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if rules.should_block(url):
            print("Заблокировано ::::::::::::::::::::::", url)
            info.block(True)


interceptor = WebEngineUrlRequestInterceptor()

class Mozarella(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # основное окно
        self.setWindowTitle("Mozarella")
        self.setWindowIcon(QIcon('salad.png'))

        # стиль контекстного меню
        self.setStyleSheet('''
            QMenu {
                background: lightBlue;
                color: black;
            }
            QMenu::item:selected {
                background: lightGray;
            }
        ''')


############### ВКЛАДКИ 
        # Определять геолокацию == False
        # self.tabs.currentWidget().page().settings().setAttribute(QWebSettings.AutoLoadImages, False)
        # self.tabs.currentWidget().page().settings().setAttribute(QWebSettings.JavascriptEnabled, False)
        #self.tabs.currentWidget() == browser объект внутри вкладки
    
        self.tabs = QTabWidget()                                          # виджет с вкладками
        self.tabs.setDocumentMode(True)                                   # внешний вид вкладок
        self.add_new_tab("about:blank", "blank")                          # сразу создаём вкладку
        self.tabs.tabBarDoubleClicked.connect(self.doubleclick_addtab)    # новая вкладка по двойному клику
        self.tabs.currentChanged.connect(self.current_tab_changed)        # изменение строки url при смене закладки
        self.tabs.setTabsClosable(True)                                   # включить возможность закрывать вкладки 
        self.tabs.tabCloseRequested.connect(self.current_tab_close)       # метод, которым вкладки будут закрываться 
        self.tor = False                                                  # tor по умолчанию выключен




################### КНОПОЧКИ И ТУЛБАР
        # основной тулбар
        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(20,20))
        navtb.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(navtb)

        # кнопка назад
        btn_back = QAction(QIcon('back.png'), 'Back', self)            # <==
        btn_back.triggered.connect(lambda: self.tabs.currentWidget().back())
        btn_back.setShortcut(QKeySequence('Backspace'))                # горячая клавиша
        navtb.addAction(btn_back)
        
        # кнопка вперёд
        btn_forward = QAction(QIcon('forward.png'), 'Forward', self)    # ==>
        btn_forward.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(btn_forward)
        
        # кнопка перехода к главной странице сайта
        btn_root = QAction(QIcon('root.png'), 'Back', self)          # ROOT
        btn_root.triggered.connect(self.go_root)
        navtb.addAction(btn_root)

        
        navtb.addSeparator()

        self.entry_url = QLineEdit()                                   # URL
        self.entry_url.editingFinished.connect(self.open_url)          # если редактирование адресной строки закончено
        # self.entry_url.returnPressed.connect(self.open_url)          # если нажат Enter в адресной строке
        navtb.addWidget(self.entry_url)

        navtb.addSeparator()

    
############ МЕНЮ НАСТРОЕК 
        menu_settings = QPushButton("", self)
        menu_settings.setIcon(QIcon("wrench.png"))
        navtb.addWidget(menu_settings)
        menu = QMenu()
        menu_settings.setMenu(menu)

        self.btn_image = QAction(QIcon("red.png"), "Disable load images", self)        # КНопка отключения изображений
        self.btn_image.setCheckable(True)
        self.btn_image.triggered.connect(self.disable_images)
        menu.addAction(self.btn_image)

        self.btn_java = QAction(QIcon("red.png"), "Disable load java", self)        # КНопка отключения изображений
        self.btn_java.setCheckable(True)
        self.btn_java.triggered.connect(self.disable_java)
        menu.addAction(self.btn_java)

        self.btn_adblock = QAction(QIcon('red.png'), 'TurnOn Adblock', self)            # RUN ADBLOCK
        self.btn_adblock.setCheckable(True)
        self.btn_adblock.triggered.connect(self.turnon_adblock)
        menu.addAction(self.btn_adblock)

        self.btn_print = QAction(QIcon('printer.png'), "Save Page to pdf file", self)
        self.btn_print.triggered.connect(self.print)
        menu.addAction(self.btn_print)
        
        self.setCentralWidget(self.tabs)      # главный виджет



    def doubleclick_addtab(self, i):
        """ Добавляет новую вкладку при двойном клике """
        if i == -1:     # двойной клик не на вкладке
            self.add_new_tab()

    def current_tab_close(self, i):
        """ настройка метода закрытия вкладок """
        if self.tabs.count() < 2:  # если осталась одна вкладка - игнорировать закрытие
            return
        self.tabs.currentWidget().stop()
        self.tabs.removeTab(i)

    def current_tab_changed(self, i):
        """ Изменяет адресную строку в зависимости от того какая вкладка выбрана """
        url = self.tabs.currentWidget().url()
        self.update_entry_url(url, self.tabs.currentWidget())
   

    def add_new_tab(self, url = "", label = "blank"):
        """ функция добавляет новую вкладку и создаёт в ней объект browser """
        browser = QWebView()
        browser.setUrl(QUrl(url))
        browser.urlChanged.connect(lambda url, browser = browser: self.update_entry_url(url, browser))         # действия при изменении url

        browser.page().settings().setAttribute(QWebSettings.AllowGeolocationOnInsecureOrigins, False)   # отключить геолокацию!

        currenttab = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(currenttab)           # сделать текущую вкладку активной

        # изменить имя вкладки, когда загрузка завершена!
        browser.loadFinished.connect(lambda _, i=currenttab, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

        browser.contextMenuEvent = self.mycontextMenuEvent     # своё контекстное меню



    def mycontextMenuEvent(self, event):
        """ своё контекстное меню при нажатии правой кнопки """
        menu = self.tabs.currentWidget().page().createStandardContextMenu()    # за основу берём стандартное меню
        # menu = QMenu(self)                                                   # или создаём своё с нуля

        # для открытия линка под курсором в новой вкладке
        opentab = menu.addAction("&Open in new tab")
        url = self.tabs.currentWidget().page().contextMenuData().linkUrl()     # чтение url под курсором
        if url:
            opentab.triggered.connect(lambda : self.add_new_tab(url))

        # для скачивания файла под курсором
        download_action = menu.addAction("Download file")
        if url:
            try:
                download_action.triggered.connect(lambda: self.download(url))
                print("[*] start downloading")
            except:
                print("[!] can't download")

        # для добавления записи в easylist
        block_action = menu.addAction("Block this element")
        block_action.triggered.connect(lambda: self.addToEasyList(url))

        menu.exec_(event.globalPos())

    def addToEasyList(self, link):
        with open("easylist.txt", "a") as file:
            file.writelines(link.toString())

    def download(self, url):
        """ скачивание файла через requests """

        url = url.toString()
        filename = url.split("/")[-1]
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            savefile = QFileDialog.getSaveFileName(self, 'Save File', filename, "")
            print(f"trying download {url} to {savefile[0]}")
            with open(savefile[0], 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            # Manually raise if status code is anything other than 200
            r.raise_for_status()

    def disable_images(self, a):
        ''' Отключает автоматическую загрузку изображений с сайтов '''
        print("Disable Images:", a)
        if a:
            self.btn_image.setIcon(QIcon("green.png"))
            self.tabs.currentWidget().page().settings().setAttribute(QWebSettings.AutoLoadImages, False)
        else:
            self.btn_image.setIcon(QIcon("red.png"))
            self.tabs.currentWidget().page().settings().setAttribute(QWebSettings.AutoLoadImages, True)

    def disable_java(self, a):
        ''' Отключает ява-скрипты '''
        print("Disable Java:", a)
        if a:
            self.btn_java.setIcon(QIcon("green.png"))
            self.tabs.currentWidget().page().settings().setAttribute(QWebSettings.JavascriptEnabled, False)
        else:
            self.btn_java.setIcon(QIcon("red.png"))
            self.tabs.currentWidget().page().settings().setAttribute(QWebSettings.JavascriptEnabled, True)




    def turnon_adblock(self, status):
        print("Adblock: ", status)
        """ Скачивает фильтр рекламы, передаёт его Adblock_Rules и вызывает класс WebEngineUrlRequestInterceptor """
        if status:
            ''' загружаем правила '''
            s = requests.get('https://easylist.to/easylist/easylist.txt')
            """ сохраняем в файл """
            with open("easylist.txt", "wb") as f:
                f.write(s.content)

            """ читаем из файла в кодировке utf-8 """
            raw_rules = open("easylist.txt", encoding='utf-8', errors='ignore')
            
            # скармливаем правила библиотеке adblock
            globals()['rules'] = AdblockRules(raw_rules)
            self.btn_adblock.setIcon(QIcon("green.png"))      # меняем иконку на зелёную
            QtWebEngineWidgets.QWebEngineProfile.defaultProfile().setRequestInterceptor(interceptor)   # включаем профиль
        else:

            with open("nothing.txt", "w") as f:           # пустой файл в качестве настроек adblock
                raw_rules = f.readlines()
                globals()['rules'] = AdblockRules(raw_rules)
            self.btn_adblock.setIcon(QIcon("red.png"))

    def go_root(self):
        ''' Для кнопки перехода в корень сайта '''
        url = self.entry_url.text()
        slash_object = re.finditer(pattern='/', string = url)
        indexes = [index.start() for index in slash_object]
        if len(indexes) >= 3:
            url = url[:indexes[2]]
        self.tabs.currentWidget().setUrl(QUrl(url))                             # переход по url


    def update_entry_url(self, q, browser = None):
        ''' Обновляет адресную строку на текущее местоположение '''
        if browser != self.tabs.currentWidget():
            # игнорировать, если сигнал не из этой вкладки
            return

        self.entry_url.setText(q.toString())
        self.entry_url.setCursorPosition(0)                # позиция курсора после обновления адресной строки


    def open_url(self):
        ''' отрабатывает при нажатии Enter в адресной строке '''
        url = self.entry_url.text()
        if "http://" not in url and "https://" not in url:
            url = "http://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))                             # переход по url

    def print(self):
        """ Открывает диалоговое окно для выбора куда сохранить файл и сохраняет страницу в pdf """
        name = QFileDialog.getSaveFileName(self, 'Save File', "page", "PDF files (*.pdf)")
        self.tabs.currentWidget().page().printToPdf(f"{name[0]}")




def call_tor():
    os.system(f'xterm -e bash -c "tor -f {torrc_path}"')

app = QApplication(sys.argv)
if len(sys.argv) > 1:
    if sys.argv[1] in ("-tor", "tor", "--tor", "/tor"):
        if os.name == 'posix':
            torrc_path = os.path.join("tor", "torrc")
            import multiprocessing
            p = multiprocessing.Process(target=call_tor)
            p.start()

        else:
            tor_path = os.path.join("tor", "tor.exe")
            torrc_path = os.path.join("tor", "torrc")
            os.system(f"start cmd /c {tor_path} -f {torrc_path}")
        networkProxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, "127.0.0.1", 9052)
        QNetworkProxy.setApplicationProxy(networkProxy)
    elif sys.argv[1] in ("-h", "--h", "help", "-help", "--help", "-?", "/?", "--?"):
        print(help_text)
        quit()

print(sys.argv)
window = Mozarella()
window.show()
# sys.argv.append('--disable-web-security --disable-webgl --disable-webgl2')
app.exec_()



                    ##Setting the user agent of the browser.
        #chrome = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36"
        #edge = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4482.0 Safari/537.36 Edg/92.0.874.0"
        #firefox = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        #brave = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.38 Safari/537.36 Brave/75"
        #safari = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15"
        #chromium = "Mozilla/5.0 (X11; GNU/Linux) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/88.0.4324.150 Chrome/88.0.4324.150 Safari/537.36 Tesla/DEV-BUILD-4d1a3f465b3a"

        #user_agent_string = safari

        #self.tabs.currentWidget().page().profile().setHttpUserAgent(
            #user_agent_string
        #)















