import os
import secrets
import sys
from PyQt5 import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from bs4 import BeautifulSoup
import requests
import webbrowser as wb
from lxml import etree,html
from secrets import *

from ui_main import *
import time

import pandas as pd


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        self.ui.lineEdit.textChanged.connect(self.AutoSearchEnginebyUser)
        
        self.url = {'jumia':[],'Mega pc':[],'tunisianet':[]}


        with open('link.txt','r',encoding='utf-8') as file:
            for i in file:
                url = i.replace('\n','')

                if 'jumia.com' in url:
                    self.url['jumia'].append(url)

                elif 'tunisianet.com.tn' in url:
                    self.url['tunisianet'].append(url)

                elif 'megapc.tn' in url:
                    self.url['Mega pc'].append(url)



        
        self.listvalues = {}
        self.filterx = []

        try:
            self.AutoSearchEnginebySystem()
        except requests.exceptions.ConnectionError:
            self.dialogueWidget('No Connection Found','Exit')
        



        self.ui.pushButton.clicked.connect(self.AutoSystemCheking)

        self.ui.pushButton_3.clicked.connect(lambda : self.ui.stackedWidget.setCurrentWidget(self.ui.page))






    def AutoSystemCheking(self):
        self.url = {'jumia':[],'tunisianet':[],'Mega pc':[]}


        with open('link.txt','r',encoding='utf-8') as file:
            for i in file:
                url = i.replace('\n','')

                if 'jumia.com' in url:
                    self.url['jumia'].append(url)

                elif 'tunisianet.com.tn' in url:
                    self.url['tunisianet'].append(url)

                elif 'megapc.tn' in url:
                    self.url['Mega pc'].append(url)



        
        self.listvalues = {}
        self.filterx = []
        try:
            self.AutoSearchEnginebySystem()
        except requests.exceptions.ConnectionError:
            self.dialogueWidget('No Connection Found','Exit')

    def stackSwitch(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)




    def AutoSearchEnginebySystem(self):
        self.header = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0"}
        for key in self.url.keys():
            self.listvalues[key] = []
            ProductName = []
            ProductPrice = []
            ProductPricefxed = []
            ProductPriceFilter = []
            ProductUrl = []
            ProductInfo = []

            for url in self.url[key]:
                req = requests.get(url, headers=self.header)
                soup = BeautifulSoup(req.content, 'lxml')


                if key == 'jumia':
                    #find title of product
                    showName = soup.find_all('h3',{'class':'name'})

                    #find price of product
                    showPrice = soup.find_all('div',{'class':'prc'})

                    #find link of product
                    for urlItem in soup.select("[class='prd _fb col c-prd'] a"):
                        urlItem = urlItem['href']
                        if urlItem[0] == '/':
                            ProductUrl.append(str(url[0:24]+urlItem))

                    


                elif key == 'Mega pc':
                    #find title of product
                    showName = soup.find_all('p',{'class':'title-prod'})

                    #find price of product
                    showPrice = soup.find_all('div',{'class':'new-price'})

                    tree = html.fromstring(req.content) 

                    linksItem = []
                    links = []

                    showlink = soup.findAll('div',{'class':'card'})
                    for i in showlink:
                        linksItem.append(i.findAll('a')[0])
                        
                    lenLinks = len(linksItem)

                    # Get element using XPath
                    for i in range(lenLinks):
                        link = tree.xpath(f'/html/body/app-root/app-content-layout/div/div/div/div/main/app-shop/app-produits-par-sous-categ/section/div/div/div/div/div[2]/div/div/div/div/div/div/div[{i}]/div/div/a/@href')
                        if link:
                            links.append('https://megapc.tn'+link[0])
                            
                    for url in links:
                        ProductUrl.append(str(url))
                            



                elif key == 'tunisianet':
                    #find title of product
                    showName = soup.find_all('h2',{'class':'h3 product-title'})

                    #find price of product
                    showPrice = soup.find_all('span',{'class':'price'})

                    #find title of product
                    showUrl = soup.select('h2.h3.product-title a')
                    #find link of product
                    for UrlItem in showUrl:
                        ProductUrl.append(UrlItem.get('href'))

               

                else:
                    pass
                
                if key == 'tunisianet':
                    for i in range(0,len(showPrice),2):
                        ProductPricefxed.append(showPrice[i])
                    showPrice = ProductPricefxed    
                    
                print(len(showName))
                print(len(showPrice))
                
                for i in range(len(showName)):
                    ProductName.append(showName[i].text.strip("\n").strip('\t').strip(''))
                    ProductPrice.append(showPrice[i].text.strip("\n").strip('\t').strip(''))
                ProductName = list(filter(None, ProductName))
                ProductPrice = list(filter(None, ProductPrice))
                
                for Price in ProductPrice:
                    ProductPriceFilter.append(float(self.fnfilter(key,Price)))

                

                ProductUrl = list(filter(None, ProductUrl))
                ProductInfo = list(filter(None, ProductInfo))
                #print(key,":",val)
                self.listvalues[key].clear()
                self.listvalues[key].append(ProductName)
                self.listvalues[key].append(ProductPriceFilter)
                self.listvalues[key].append(ProductUrl)
                self.listvalues[key].append(ProductInfo)

                

                data = {'ProductName':ProductName,'ProductPriceFilter':ProductPriceFilter,'ProductUrl':ProductUrl}

                df = pd.DataFrame(data,columns=[key for key in data.keys()])
                try:
                    os.mkdir('website')
                except:
                    pass
                df.to_csv(f'website/{key}.csv')

        


        """AutoNameProductCompelter = [] 
        for key in self.listvalues.keys():
            listvalues = pd.read_csv(f'website/{key}.csv')
            for item in listvalues['ProductName']:
                AutoNameProductCompelter.append(item)
                        
        
        completer = QCompleter(AutoNameProductCompelter)
        self.ui.lineEdit.setCompleter(completer)"""

        del self.listvalues
            
        
    def AutoSearchEnginebyUser(self):

        maxList = []

        try:
            while True:
                itemG = self.ui.verticalLayout.takeAt(0)
                if not itemG:
                    break
                self.ui.verticalLayout.removeWidget(itemG.widget())
        except AttributeError:
            pass

        UserInput = self.ui.lineEdit.text()
        UserInput = UserInput.split()

        row = 0
        for key in self.url.keys():
            col = 0
            l = len(UserInput)
            
            listvalues = pd.read_csv(f'website/{key}.csv')


            for e,item in enumerate(listvalues['ProductName']):
                d = 0
                """iteminput = UserInput[0:UserInput.find(i)]
                UserInput = UserInput[UserInput.find(i)+1:]"""
                for s in UserInput:
                    if s.upper() in listvalues['ProductName'][e].upper():
                        d += 1
                    else:
                        d+= 0
                    
                if d == l:
                    self.contentWidgetProduct(row,listvalues['ProductPriceFilter'][e],listvalues['ProductName'][e],listvalues['ProductUrl'][e],key)
                    maxList.append(listvalues['ProductPriceFilter'][e])
                else:
                    pass
                        
                row += 1
                col += 1

        try:
        
            maxx = max(maxList)
            minn = min(maxList)
        except:
            pass


            
        
        
        try:
            for key in self.url.keys():
                listvalues = pd.read_csv(f'website/{key}.csv')
                for p,item in enumerate(listvalues['ProductName']):
                    if maxx == float(listvalues['ProductPriceFilter'][p]):
                        itemTitle = item[0:34]+'\n'+item[34:len(item)]
                        try:
                            while True:
                                itemG = self.ui.verticalLayout_3.takeAt(0)
                                if not itemG:
                                    break
                                self.ui.verticalLayout_3.removeWidget(itemG.widget())
                        except AttributeError:
                            pass
                        self.ContentSatisticsWidget('max',0,key,itemTitle,maxx,listvalues['ProductUrl'][p])
                    else:
                        try:
                            while True:
                                itemG = self.ui.verticalLayout_2.takeAt(0)
                                if not itemG:
                                    break
                                self.ui.verticalLayout_2.removeWidget(itemG.widget())
                        except AttributeError:
                            pass

            

            for key in self.url.keys():
                listvalues = pd.read_csv(f'website/{key}.csv')
                for p,item in enumerate(listvalues['ProductName']):
                    if minn == float(listvalues['ProductPriceFilter'][p]):
                        itemTitle = item[0:34]+'\n'+item[34:len(item)]
                        try:
                            while True:
                                itemG = self.ui.verticalLayout_3.takeAt(1)
                                if not itemG:
                                    break
                                self.ui.verticalLayout_3.removeWidget(itemG.widget())
                        except AttributeError:
                            pass
                        self.ContentSatisticsWidget('min',1,key,itemTitle,minn,listvalues['ProductUrl'][p]) 
                    else:
                        try:
                            while True:
                                itemG = self.ui.verticalLayout_2.takeAt(0)
                                if not itemG:
                                    break
                                self.ui.verticalLayout_2.removeWidget(itemG.widget())
                        except AttributeError:
                            pass

        except UnboundLocalError:
            pass

            

        

    def showIinfoWidget(self,Purl,key):
        print(Purl)
        self.ui.textBrowser.clear()
        if key == 'jumia':
            req = requests.get(Purl, headers=self.header)
            soup = BeautifulSoup(req.content, 'lxml')
            info = soup.find('div',{'class':'markup -mhm -pvl -oxa -sc'})
            try:
                self.ui.textBrowser.setPlainText(info.text)
            except AttributeError:
                self.ui.textBrowser.setPlainText('no information detected')
        

        elif key == 'Mega pc':
            req = requests.get(Purl, headers=self.header)
            soup = BeautifulSoup(req.content, 'lxml')
            info = soup.find('div',{'class':'p-datatable-wrapper'})
            try:
                self.ui.textBrowser.setPlainText(info.text)
            except AttributeError:
                self.ui.textBrowser.setPlainText('no information detected')


        elif key == 'tunisianet':
            req = requests.get(Purl, headers=self.header)
            soup = BeautifulSoup(req.content, 'lxml')
            info = soup.find("div",{'class':'prodes'})
            try:
                self.ui.textBrowser.setPlainText(info.text)
            except AttributeError:
                self.ui.textBrowser.setPlainText('no information detected')

        else:
            pass

        

            


    def fnfilter(self,key,Price):
        try:
            newListPrice = []
            if key in ['jumia','Mega pc']:
                newPrice = ''
                for j in Price:
                    if j in ['0','1','2','3','4','5','6','7','8','9','.']:
                        newPrice += j
                newListPrice.append(str(float(newPrice)))

            elif key in ['tunisianet','mytek']:
                newPrice = ''
                for j in Price:
                    if j in ['0','1','2','3','4','5','6','7','8','9',',']:
                        newPrice += j
                newPrice = newPrice[0:newPrice.find(',')]+'.'+newPrice[-3:]
                newListPrice.append(str(float(newPrice)))
            return newPrice

        except ValueError:
            print("ERROR")


    def contentWidgetProduct(self,row,price,title,url,key):
        self.frame = QtWidgets.QFrame(self.ui.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(600, 200))
        self.frame.setSizeIncrement(QtCore.QSize(0, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(31, 31, 480, 41))
        self.label_2.setStyleSheet("font-size:12px;")
        self.label_2.setObjectName("label_2")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 90, 101, 23))
        self.pushButton_2.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";\n"
"color: black;background:none;border:none;")
        self.pushButton_2.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f"src/{key}.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setIconSize(QtCore.QSize(80, 16))
        self.pushButton_2.setToolTip(f"{key}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(30, 130, 111, 20))
        self.label_3.setStyleSheet("font: 14pt \"MS Shell Dlg 2\";\n"
"font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_3.setObjectName("label_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.frame)
        self.pushButton_4.setGeometry(QtCore.QRect(10, 170, 75, 23))
        self.pushButton_4.setStyleSheet("background-color: rgb(27, 78, 117);\n"
"border-radius:10px;\n"
"color: rgb(255, 255, 255);")
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame)
        self.pushButton_5.setGeometry(QtCore.QRect(100, 170, 75, 23))
        self.pushButton_5.setStyleSheet("background-color: rgb(195, 31, 31);\n"
"border-radius:10px;\n"
"color: rgb(255, 255, 255);")
        self.pushButton_5.setObjectName("pushButton_5")

        self.label_2.setText(title)
        self.label_3.setText(str(price))

        self.pushButton_4.setText('Show info')
        self.pushButton_5.setText('Acheter')

        self.ui.verticalLayout.addWidget(self.frame, row, QtCore.Qt.AlignHCenter)
        self.pushButton_4.clicked.connect(self.stackSwitch)
        self.pushButton_4.clicked.connect(lambda : self.showIinfoWidget(url,key))
        self.pushButton_5.clicked.connect(lambda : wb.open(url))
        self.ui.pushButton_3.clicked.connect(lambda : self.ui.stackedWidget.setCurrentWidget(self.ui.page))




    def ContentSatisticsWidget(self,typeWidget,row,key,name,price,url):
        self.frameSatistics = QtWidgets.QFrame(self.ui.scrollAreaWidgetContents_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameSatistics.sizePolicy().hasHeightForWidth())
        self.frameSatistics.setSizePolicy(sizePolicy)
        self.frameSatistics.setMinimumSize(QtCore.QSize(220, 150))
        self.frameSatistics.setSizeIncrement(QtCore.QSize(0, 0))
        self.frameSatistics.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameSatistics.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameSatistics.setObjectName("frameSatistics")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frameSatistics)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.verticalLayout_2.setSpacing(2)
        self.type = QtWidgets.QLabel(self.frameSatistics)
        self.type.setAlignment(QtCore.Qt.AlignCenter)
        self.type.setObjectName("type")
        self.verticalLayout_2.addWidget(self.type)
        self.ProductNameLabel = QtWidgets.QLabel(self.frameSatistics)
        self.ProductNameLabel.setObjectName("ProductNameLabel")
        self.verticalLayout_2.addWidget(self.ProductNameLabel)
        self.ProductsiteLogo = QtWidgets.QPushButton(self.frameSatistics)
        self.ProductsiteLogo.setStyleSheet("border-radius:none;\n"
"background-color:none;padding:5px;")
        self.ProductsiteLogo.setText("")
        self.ProductsiteLogo.setObjectName("ProductsiteLogo")
        self.verticalLayout_2.addWidget(self.ProductsiteLogo)
        self.ProductPriceLabel = QtWidgets.QLabel(self.frameSatistics)
        self.ProductPriceLabel.setObjectName("ProductPriceLabel")
        self.verticalLayout_2.addWidget(self.ProductPriceLabel)
        self.buttonShowInfoProduct = QtWidgets.QPushButton(self.frameSatistics)
        self.buttonShowInfoProduct.setText("Show info")
        self.buttonShowInfoProduct.setObjectName("buttonShowInfoProduct")
        self.verticalLayout_2.addWidget(self.buttonShowInfoProduct)
        self.buttonGetPrduct = QtWidgets.QPushButton(self.frameSatistics)
        self.buttonGetPrduct.setText("Acheter")
        self.buttonGetPrduct.setObjectName("buttonGetPrduct")
        self.verticalLayout_2.addWidget(self.buttonGetPrduct)
        self.ui.verticalLayout_3.addWidget(self.frameSatistics, row, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)


        self.type.setText(f'{typeWidget}')
        self.ProductNameLabel.setText(f"{name}")
        self.ProductPriceLabel.setText(f"{price}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f"src/{key}.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ProductsiteLogo.setText("")
        self.ProductsiteLogo.setIcon(icon)
        self.ProductsiteLogo.setStyleSheet("font: 50pt \"MS Shell Dlg 2\";\n"
"color: black;background:none;border:none;padding:5px;")
        self.ProductsiteLogo.setIconSize(QtCore.QSize(80, 16))
        

        self.buttonShowInfoProduct.clicked.connect(self.stackSwitch)
        self.buttonShowInfoProduct.clicked.connect(lambda : self.showIinfoWidget(url,key))
        self.buttonShowInfoProduct.setStyleSheet("background-color: rgb(27, 78, 117);\n"
"border-radius:10px;\n")
        self.buttonGetPrduct.clicked.connect(lambda : wb.open(url))
        self.buttonGetPrduct.setStyleSheet("background-color: rgb(195, 31, 31);\n"
"border-radius:10px;\n"
"color: rgb(255, 255, 255);")
        self.ui.pushButton_3.clicked.connect(lambda : self.ui.stackedWidget.setCurrentWidget(self.ui.page))








app = QApplication(sys.argv)
win = MainWindow()
try:
    win.setStyleSheet(str(open('style.css','r').read()))
except:
    sys.exit()
win.show()
sys.exit(app.exec_())
