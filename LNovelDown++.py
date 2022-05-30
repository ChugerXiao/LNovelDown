# -*- coding: utf-8 -*-
from requests import get, codes
from bs4 import BeautifulSoup as Bs
from sys import exit, argv
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject, QStringListModel
from src.LNovelDown import Ui_MainWindow
from src.Search import Ui_Dialog as Ui_Search
from src.Reset import Ui_Dialog as Ui_Reset
from src.Set import Ui_Dialog as Ui_Set
import src.images_rc
from parse import parse
from time import sleep
from threading import Thread, Semaphore
from os import mkdir, path, remove, listdir, rmdir, _exit, system
from subprocess import Popen, PIPE, STDOUT
from json import loads, dumps
from pyperclip import copy


class Signal(QObject):
    send = pyqtSignal(str, str)
    sendSet = pyqtSignal()

    def __init__(self):
        super(Signal, self).__init__()

    def sendMessageBox(self):
        self.send.emit('错误', '未连接到站点，请重试')

    def sendMessageBox_2(self):
        self.send.emit('错误', '没有网络连接，请重试')

    def sendMessageBox_3(self):
        self.send.emit('错误', '初始化错误，请重启')

    def sendSetText(self):
        self.sendSet.emit()


class searchWindow(QDialog, Ui_Search):
    def __init__(self):
        super(searchWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/novel.ico'))
        self.names = []
        self.authors = []
        self.publishers = []
        self.states = []
        self.types = []
        self.words = []
        self.remarks = []
        self.urls = []
        self.url = ''
        self.bookName = ''
        self.index = 0
        self.comboBox.addItems(['书名', 'BID'])

    def search(self):
        thread = Thread(target=self.searchTread, args=())
        thread.start()

    def searchTread(self):
        self.clearAll()
        self.setAllEnable(False)
        self.lineEdit.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton.setText('搜索中…')
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        try:

            if self.comboBox.currentText() == '书名':
                with open('temp/config.json', 'r') as file:
                    config = loads(file.read())
                searchUrl = config['searchUrl']
                params = {
                    'searchkey': self.lineEdit.text(),
                    'searchtype': 'all',
                }
                headers = {'Cookie': config['Cookie']}
                searchRes = get(searchUrl, params=params, timeout=10, headers=headers)
            elif self.comboBox.currentText() == 'BID':
                searchUrl = f'https://www.linovelib.com/novel/{self.lineEdit.text()}.html'
                searchRes = get(searchUrl, timeout=10)
            else:
                raise FileNotFoundError
            if searchRes.status_code != codes.ok: raise TimeoutError
            searches = Bs(searchRes.text, 'html.parser').find_all('div', class_="fl se-result-infos")
            if len(searches) == 0:
                searches = Bs(searchRes.text, 'html.parser').find_all('div', class_="book-detail clearfix")
                if len(searches) == 1:
                    self.setAllEnable(True)
                    self.pushButton_2.setEnabled(False)
                    self.pushButton_3.setEnabled(False)
                    name = Bs(str(searches[0]), 'html.parser').find_all('h1', class_="book-name")[0].text
                    author = Bs(searchRes.text, 'html.parser').find_all('div', class_="au-name")[0].text
                    publisher = Bs(str(searches[0]), 'html.parser').find_all('a', class_="label")[0].text
                    state = Bs(str(searches[0]), 'html.parser').find_all('a', class_="state")[0].text
                    Type = Bs(str(searches[0]), 'html.parser').find_all('span')[0].text.strip()
                    word = Bs(str(searches[0]), 'html.parser').find_all('div', class_="nums")
                    word = Bs(str(word[0]), 'html.parser').find_all('i')[0].text
                    remark = Bs(str(searches[0]), 'html.parser').find_all('p')[0].text
                    url = Bs(searchRes.text, 'html.parser').find_all('a', class_="btn read-btn")[0].get('href')
                    self.lineEdit_2.setText(name)
                    self.lineEdit_3.setText(author)
                    self.lineEdit_6.setText(publisher)
                    self.lineEdit_5.setText(state)
                    self.lineEdit_4.setText(Type)
                    self.lineEdit_7.setText(word)
                    self.plainTextEdit.setPlainText(remark)
                    self.url = 'www.linovelib.com' + url
            else:
                for each in searches:
                    name = Bs(str(each), 'html.parser').find_all('h2', class_="tit")[0].text
                    bookInfo = Bs(str(each), 'html.parser').find_all('div', class_='bookinfo')[0]
                    bookInfos = Bs(str(bookInfo), 'html.parser').find_all('a')
                    author = bookInfos[0].text
                    publisher = bookInfos[1].text
                    bookInfos = Bs(str(bookInfo), 'html.parser').find_all('span')
                    state = bookInfos[0].text
                    Type = Bs(str(each), 'html.parser').find_all('div', class_='key-word')[0].text.strip()
                    word = ''
                    remark = Bs(str(each), 'html.parser').find_all('p')[0].text
                    url = Bs(str(each), 'html.parser').find_all('a')[0].get('href').replace('.html', '/catalog')
                    self.names.append(name)
                    self.authors.append(author)
                    self.publishers.append(publisher)
                    self.states.append(state)
                    self.types.append(Type)
                    self.words.append(word)
                    self.remarks.append(remark)
                    self.urls.append(url)
                self.setAllText()
                self.setAllEnable(True)
                self.pushButton_2.setEnabled(False)
                if len(self.names) > 1:
                    self.pushButton_3.setEnabled(True)
                else:
                    self.pushButton_3.setEnabled(False)
        except TimeoutError:
            signal = Signal()
            signal.send.connect(self.slotMessageBox)
            signal.sendMessageBox()
        except Exception:
            signal = Signal()
            signal.send.connect(self.slotMessageBox)
            signal.sendMessageBox_2()
        except FileNotFoundError:
            signal = Signal()
            signal.send.connect(self.slotMessageBox)
            signal.sendMessageBox_3()
        finally:
            self.lineEdit.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton.setText('搜索')

    def up(self):
        self.index = self.index - 1
        self.pushButton_3.setEnabled(True)
        if self.index == 0:
            self.pushButton_2.setEnabled(False)
        self.setAllText()

    def down(self):
        self.index = self.index + 1
        self.pushButton_2.setEnabled(True)
        if self.index == len(self.names) - 1:
            self.pushButton_3.setEnabled(False)
        self.setAllText()

    def finish(self):
        self.bookName = self.lineEdit_2.text()
        self.close()

    def setAllEnable(self, enable):
        self.lineEdit_2.setEnabled(enable)
        self.lineEdit_3.setEnabled(enable)
        self.lineEdit_4.setEnabled(enable)
        self.lineEdit_5.setEnabled(enable)
        self.lineEdit_6.setEnabled(enable)
        self.lineEdit_7.setEnabled(enable)
        self.plainTextEdit.setEnabled(enable)
        self.pushButton_4.setEnabled(enable)

    def clearAll(self):
        self.names = []
        self.authors = []
        self.publishers = []
        self.states = []
        self.types = []
        self.words = []
        self.remarks = []
        self.urls = []
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_6.clear()
        self.lineEdit_5.clear()
        self.lineEdit_4.clear()
        self.lineEdit_7.clear()
        self.plainTextEdit.clear()
        self.url = ''
        self.bookName = ''
        self.index = 0

    def setAllText(self):
        self.lineEdit_2.setText(self.names[self.index])
        self.lineEdit_3.setText(self.authors[self.index])
        self.lineEdit_6.setText(self.publishers[self.index])
        self.lineEdit_5.setText(self.states[self.index])
        self.lineEdit_4.setText(self.types[self.index])
        self.lineEdit_7.setText(self.words[self.index])
        self.plainTextEdit.setPlainText(self.remarks[self.index])
        self.url = 'www.linovelib.com' + self.urls[self.index]

    def slotMessageBox(self, title, text):
        QMessageBox.critical(self, title, text, QMessageBox.Ok)


class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setupUi(self)
        self.initJson()
        self.setWindowIcon(QIcon(':/novel.ico'))
        self.pools = Semaphore(8)
        self.search = searchWindow()
        self.reset = resetWindow()
        self.set = setWindow()
        self.cleanWindow = QMessageBox()
        self.cleanButton = self.cleanWindow.addButton('完成', QMessageBox.YesRole)
        self.choice = ''
        self.url = ''
        self.bookName = ''
        self.setText = ''
        self.urls = []
        self.chapters = []
        self.failedIndex = []
        thread = Thread(target=self.ping, args=())
        # thread.setDaemon()
        thread.start()
        # self.debug()

    def ping(self):
        self.statusbar.showMessage('    检测源站延迟中。。。')
        while True:
            output = Popen('ping www.linovelib.com', stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=True)
            lines = output.stdout.readlines()
            bagRate = parse('{}({} 丢失){}', lines[8].decode("gbk"))[1]
            speed = parse('{}平均 = {}', lines[10].decode("gbk"))[1]
            try:
                self.statusbar.showMessage(f'    丢包率：{bagRate}{" " * 10}延迟：{speed}')
            except:
                self.statusbar.showMessage('    持续掉线中。。。')

    def debug(self):
        self.url = 'www.linovelib.com/novel/2765/catalog'
        self.bookName = '关于邻家的天使大人不知不觉把我惯成了废人这档子事'
        self.urls = ['/novel/2765/131667.html', '/novel/2765/131668.html', '/novel/2765/131669.html']
        self.chapters = ['01 天使大人是娇嫩欲滴的女人', '02 天使大人的提案', '03 天使大人照料病人']
        self.pushButton_3.setEnabled(True)
        self.listView.setEnabled(True)
        self.checkBox.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.setListView(self.chapters)

    @staticmethod
    def initJson():
        try:
            if not path.isdir('temp'): mkdir('temp')
            with open('temp/config.json', 'r') as file:
                config = loads(file.read())
            if not ('searchUrl' in config and 'Cookie' in config):
                raise FileNotFoundError
        except:
            try:
                remove('temp/config.json')
            except:
                pass
            config = {
                'searchUrl': 'https://www.linovelib.com/S0/',
                'Cookie': 'Hm_lvt_d29ecd95ff28d58324c09b9dc0bee919=1648556726; PHPSESSID=tanlhknl6l1s8hiff6prlaidtp; jieqiUserInfo=jieqiUserId%3D457275%2CjieqiUserUname%3Dlinovelib_leo%2CjieqiUserName%3Dlinovelib_leo%2CjieqiUserGroup%3D3%2CjieqiUserGroupName%3D%E6%99%AE%E9%80%9A%E4%BC%9A%E5%91%98%2CjieqiUserVip%3D0%2CjieqiUserHonorId%3D1%2CjieqiUserHonor%3D%E5%A4%A9%E7%84%B6%2CjieqiUserToken%3Dff210ad355fecacfc819ed78980f5f6c%2CjieqiCodeLogin%3D0%2CjieqiCodePost%3D0%2CjieqiUserLogin%3D1648556894; jieqiVisitInfo=jieqiUserLogin%3D1648556894%2CjieqiUserId%3D457275; jieqiVisitId=article_articleviews%3D3181%7C3143%7C2939%7C2499%7C2547%7C1410%2Carticle_articledowns%3D2499; Hm_lpvt_d29ecd95ff28d58324c09b9dc0bee919=1648557125'
            }
            with open('temp/config.json', 'a')as file:
                file.write(dumps(config))

    def getNovel(self):
        self.search.clearAll()
        self.search.setAllEnable(False)
        self.search.pushButton_2.setEnabled(False)
        self.search.pushButton_3.setEnabled(False)
        self.search.lineEdit.clear()
        self.search.exec()
        if self.search.bookName == '': return
        self.url, self.bookName = self.search.url, self.search.bookName
        self.lineEdit.setText(self.bookName)
        self.refresh()

    def refresh(self):
        thread = Thread(target=self.refreshThread, args=())
        thread.start()

    def refreshThread(self):
        self.chapters = []
        self.urls = []
        self.lineEdit.setEnabled(False)
        self.pushButton.setText('获取中…')
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.checkBox.setEnabled(False)
        self.checkBox.setChecked(False)
        self.setListView(self.chapters)
        self.listView.setEnabled(False)
        self.plainTextEdit.clear()
        self.plainTextEdit.setEnabled(False)
        try:
            context = get('https://' + self.url, timeout=10)
            items = Bs(context.text, 'html.parser').find_all('ul', class_="chapter-list clearfix")[0]
            chapters = [each.text for each in Bs(str(items), 'html.parser').find_all('div')]
            sections = [each.text for each in Bs(str(items), 'html.parser').find_all('a') if each.text != '插图']
            self.urls = [each.get('href') for each in Bs(str(items), 'html.parser').find_all('a') if each.text != '插图']
            itemList = str(items).split('\n')
            itemList = [each for each in itemList if
                        each.find('插图') == -1 and (each.find('div') != -1 or each.find('href') != -1)]
            cIndex = sIndex = -1
            for each in itemList:
                if each.find('div') != -1:
                    cIndex = cIndex + 1
                elif each.find('href') != -1:
                    sIndex = sIndex + 1
                    self.chapters.append(chapters[cIndex] + ' ' + sections[sIndex])
            self.checkBox.setEnabled(True)
            if len(self.urls) == 0:
                self.pushButton_2.setEnabled(False)
            else:
                self.pushButton_2.setEnabled(True)
            self.listView.setEnabled(True)
            self.setListView(self.chapters)
        except:
            signal = Signal()
            signal.send.connect(self.slotMessageBox)
            signal.sendMessageBox_2()
        finally:
            self.lineEdit.setEnabled(True)
            self.pushButton.setText('查找')
            self.pushButton.setEnabled(True)
            self.pushButton_3.setEnabled(True)

    def view(self, QModelIndex):
        if not self.checkBox.isChecked(): return
        thread = Thread(target=self.viewThread, args=(QModelIndex.row(),))
        thread.start()

    def viewThread(self, clickRow):
        self.lineEdit.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.checkBox.setEnabled(False)
        self.listView.setEnabled(False)
        try:
            context = get('https://www.linovelib.com' + self.urls[clickRow], timeout=10)
            text = Bs(context.text, 'html.parser').find_all('div', id="TextContent")[0]
            self.setText = '\n'.join('    ' + each.text for each in Bs(str(text), 'html.parser').find_all('p'))
            self.plainTextEdit.setEnabled(True)
            signal = Signal()
            signal.sendSet.connect(self.slotSetText)
            signal.sendSetText()
        except:
            signal = Signal()
            signal.send.connect(self.slotMessageBox)
            signal.sendMessageBox_2()
        finally:
            self.lineEdit.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.checkBox.setEnabled(True)
            self.listView.setEnabled(True)

    def down(self):
        if not path.isdir('temp'): mkdir('temp')
        if not path.isdir('temp/' + self.bookName): mkdir('temp/' + self.bookName)
        try:
            if path.exists(self.bookName + '.txt'): remove(self.bookName + '.txt')
        except:
            QMessageBox.critical(self, '错误', '文件被占用', QMessageBox.Ok)
            return
        for each in listdir('temp/' + self.bookName):
            try:
                if path.exists(f'temp/{self.bookName}/{each}'): remove(f'temp/{self.bookName}/{each}')
            except:
                QMessageBox.critical(self, '错误', '文件被占用', QMessageBox.Ok)
                return
        thread = Thread(target=self.downThread, args=())
        thread.start()

    def downThread(self):
        signal = Signal()
        signal.sendSet.connect(self.slotBegin)
        signal.sendSetText()
        thread = [Thread(target=self.downThreads, args=(each, self.urls[each])) for each in range(len(self.chapters))]
        for each in range(len(thread)):
            thread[each].start()
            sleep(0.1)
        for each in range(len(self.chapters)):
            thread[each].join()
            self.pushButton_2.setText(f'{int((each + 1) / len(self.chapters) * 100)}%')
        signal = Signal()
        signal.sendSet.connect(self.slotMessageBoxFin)
        signal.sendSetText()

    def downThreads(self, index, href):
        with self.pools:
            self.downThreadsPool(index, href)

    def downThreadsPool(self, index, href):
        if href.find('_') == -1:
            with open(f'temp/{self.bookName}/{index}', 'a', encoding='utf-8') as file:
                if index == 0:
                    file.writelines(f'    {self.chapters[index]}\n\n')
                else:
                    file.writelines(f'\n\n\n\n    {self.chapters[index]}\n\n')
        context = self.get('https://www.linovelib.com' + href, 5, 12)
        if context == 'Failed':
            self.failedIndex.append(index)
            return
        text = Bs(context.text, 'html.parser').find_all('div', id="TextContent")[0]
        text = '\n'.join('    ' + each.text for each in Bs(str(text), 'html.parser').find_all('p'))
        if href.find('_') != -1: text = text[4:]
        with open(f'temp/{self.bookName}/{index}', 'a', encoding='utf-8') as f:
            f.writelines(text.replace('\n    （本章未完）', ''))
        href = Bs(context.text, 'html.parser').find_all('p', class_="mlfy_page")[0]
        href = Bs(str(href), 'html.parser').find_all('a')
        href = href[len(href) - 1].get('href')
        if href.find('_') != -1:
            self.downThreadsPool(index, href)

    def setListView(self, newList):
        listModel = QStringListModel()
        listModel.setStringList(newList)
        self.listView.setModel(listModel)

    @staticmethod
    def get(url, timeout, times=-1):
        while times:
            try:
                times = times - 1
                context = get(url, timeout=timeout)
                return context
            except:
                pass
        return 'Failed'

    def slotBegin(self):
        self.lineEdit.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setText('下载中…')
        self.pushButton_3.setEnabled(False)
        self.checkBox.setEnabled(False)
        self.listView.setEnabled(False)
        self.plainTextEdit.setEnabled(False)

    def slotFinish(self):
        try:
            for each in listdir('temp/' + self.bookName):
                remove(f'temp/{self.bookName}/{each}')
            rmdir(f'temp' / {self.bookName})
            rmdir('temp')
        except:
            pass
        self.url = ''
        self.bookName = ''
        self.setText = ''
        self.urls = []
        self.chapters = []
        self.failedIndex = []
        self.setListView(self.chapters)
        self.lineEdit.clear()
        self.plainTextEdit.clear()
        self.pushButton_2.setText('下载')
        self.checkBox.setChecked(False)
        self.pushButton.setEnabled(True)
        self.lineEdit.setEnabled(True)

    def slotMessageBox(self, title, text):
        QMessageBox.critical(self, title, text, QMessageBox.Ok)

    def slotMessageBoxFin(self):
        if not self.failedIndex:
            QMessageBox.information(self, '成功', f'《{self.bookName}》下载成功', QMessageBox.Ok)
        else:
            self.choice = QMessageBox.critical(self, '错误', f'《{self.bookName}》下载完成，有{len(self.failedIndex)}处错误',
                                               QMessageBox.Retry | QMessageBox.Reset | QMessageBox.Cancel,
                                               QMessageBox.Retry)
            if self.choice == QMessageBox.Retry:
                Thread(target=self.retry, args=()).start()
                return
            elif self.choice == QMessageBox.Reset:
                self.reset.failedIndex = self.failedIndex
                self.reset.chapters = self.chapters
                self.reset.urls = self.urls
                self.reset.load()
                self.reset.exec()
                self.urls = self.reset.urls
                Thread(target=self.retry, args=()).start()
                return
            elif self.choice == QMessageBox.Cancel:
                pass
        with open(self.bookName + '.txt', 'a', encoding='utf-8')as book:
            for each in range(len(self.chapters)):
                with open(f'temp/{self.bookName}/{each}', 'r', encoding='utf-8')as temp:
                    book.writelines(temp.read())
        signal = Signal()
        signal.sendSet.connect(self.slotFinish)
        signal.sendSetText()

    def retry(self):
        thread = [Thread(target=self.downThreads, args=(each, self.urls[each])) for each in self.failedIndex]
        for each in self.failedIndex:
            if path.exists(f'temp/{self.bookName}/{each}'): remove(f'temp/{self.bookName}/{each}')
        self.failedIndex = []
        for each in range(len(thread)):
            thread[each].start()
            sleep(0.1)
        for each in range(len(thread)):
            thread[each].join()
            self.pushButton_2.setText(f'{int((each + 1) / len(thread) * 100)}%')
        signal = Signal()
        signal.sendSet.connect(self.slotMessageBoxFin)
        signal.sendSetText()

    def slotSetText(self):
        self.plainTextEdit.setPlainText(self.setText)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "确认退出吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            _exit(0)
        else:
            event.ignore()

    def setting(self):
        self.set.load()
        self.set.exec()

    def clean(self):
        reply = QMessageBox.question(self, '提示', '确认清除缓存吗？\n注：请勿在下载时执行。')
        if reply == QMessageBox.Yes:
            self.cleanWindow.setIcon(QMessageBox.Information)
            self.cleanWindow.setText('清理中……\n请稍候。')
            self.cleanButton.setEnabled(False)
            Thread(target=self.cleanThread).start()
            self.cleanWindow.exec_()

    def cleanThread(self):
        dirList = [each for each in listdir('temp') if each not in ['config.json']]
        for each in dirList:
            system(f'echo y| rmdir /s temp\\{each}')
        self.cleanWindow.setText('清理完毕')
        self.cleanButton.setEnabled(True)


class resetWindow(QDialog, Ui_Reset):
    def __init__(self):
        super(resetWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/novel.ico'))
        self.failedIndex = []
        self.chapters = []
        self.urls = []
        self.index = 0

    def load(self):
        if len(self.failedIndex) > 1: self.pushButton_3.setEnabled(True)
        self.showTexts()

    def ok(self):
        self.urls[self.failedIndex[self.index]] = self.lineEdit_2.text()
        self.finish()
        self.close()

    def up(self):
        self.urls[self.failedIndex[self.index]] = self.lineEdit_2.text()
        self.index = self.index - 1
        if self.index == 0: self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(True)
        self.lineEdit_3.setEnabled(True)
        self.showTexts()

    def down(self):
        self.urls[self.failedIndex[self.index]] = self.lineEdit_2.text()
        self.index = self.index + 1
        if self.index == len(self.failedIndex) - 1: self.pushButton_3.setEnabled(False)
        self.pushButton_2.setEnabled(True)
        self.lineEdit.setEnabled(True)
        self.showTexts()

    def showTexts(self):
        if self.failedIndex[self.index] == 0:
            self.label.setText('到顶了哦')
            self.lineEdit.setText('')
            self.lineEdit.setEnabled(False)
        else:
            self.label.setText(self.chapters[self.failedIndex[self.index] - 1])
            self.lineEdit.setText(self.urls[self.failedIndex[self.index] - 1])
        if self.failedIndex[self.index] == len(self.urls) - 1:
            self.label_3.setText('到底了哦')
            self.lineEdit_3.setText('')
            self.lineEdit_3.setEnabled(False)
        else:
            self.label_3.setText(self.chapters[self.failedIndex[self.index] + 1])
            self.lineEdit_3.setText(self.urls[self.failedIndex[self.index] + 1])
        self.label_2.setText(self.chapters[self.failedIndex[self.index]])
        self.lineEdit_2.setText(self.urls[self.failedIndex[self.index]])

    def finish(self):
        self.index = 0
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)

    def copyUrl1(self):  # /novel/2356/83535.html
        copy(f'https://www.linovelib.com{self.lineEdit.text()}')

    def copyUrl2(self):
        copy(f'https://www.linovelib.com{self.lineEdit_3.text()}')


class setWindow(QDialog, Ui_Set):
    def __init__(self):
        super(setWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/novel.ico'))
        if not path.isdir('temp'): mkdir('temp')
        with open('temp/config.json', 'r') as file:
            self.config = loads(file.read())

    def load(self):
        self.lineEdit.setText(self.config['searchUrl'])
        self.lineEdit_2.setText(self.config['Cookie'])

    def save(self):
        self.config['searchUrl'] = self.lineEdit.text()
        self.config['Cookie'] = self.lineEdit_2.text()
        try:
            remove('temp/config.json')
        except:
            pass
        with open('temp/config.json', 'a') as file:
            file.write(dumps(self.config))
        self.close()


if __name__ == '__main__':
    app = QApplication(argv)

    mMainWindow = mainWindow()
    mMainWindow.show()

    exit(app.exec_())
