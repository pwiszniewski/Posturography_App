# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *

import views

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)

        self.btn_start_measure = QAction()
        # self.btn_start_measure.setGeometry(QtCore.QRect(20, 10, 89, 27))
        self.toolbar.addAction( self.btn_start_measure)

        self.btn_stop_measure = QAction()
        self.toolbar.addAction( self.btn_stop_measure)

        self.measure_time_label = QLabel('00:00')
        self.toolbar.addWidget(self.measure_time_label)

        self.toolbar.addSeparator()

        self.btn_show_liveplot = QAction("Liveplot")
        self.toolbar.addAction(self.btn_show_liveplot)

        self.btn_show_copplot = QAction("COP plot")
        self.toolbar.addAction(self.btn_show_copplot)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")

        self.openAction = QAction("&Open", self)
        self.openAction.setShortcut("Ctrl+O")

        self.saveAction = QAction("&Save", self)
        self.saveAction.setShortcut("Ctrl+S")

        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)

        self.conn_menu = self.menubar.addMenu('&Connection')
        self.port_sel_menu = self.conn_menu.addMenu("&Port")
        self.port_act_group = QActionGroup(self.port_sel_menu)
        # texts = ["Cash", "Noncash Payment", "Cash on Delivery", "Bank Transfer"]
        # for text in texts:
        #     action = QAction(text, self.port_sel_action, checkable=True, checked=text == texts[0])
        #     self.port_sel_action.addAction(action)
        #     self.port_act_group.addAction(action)
        self.port_act_group.setExclusive(True)

        self.view_menu = self.menubar.addMenu('&View')
        self.samp_range_view_menu = self.view_menu.addMenu("&Time range")
        self.samp_range_view_group = QActionGroup(self.samp_range_view_menu)
        self.refresh_view_menu = self.view_menu.addMenu("&Refresh rate")
        self.refresh_view_group = QActionGroup(self.refresh_view_menu)
        self.autscale_action = QAction("&Autoscale", self)
        self.autscale_action.setShortcut("Ctrl+A")
        self.view_menu.addAction(self.autscale_action)
        # self.port_sel_action = QAction("&Port", self)
        # self.port_sel_action
        # self.conn_menu.addAction(self.port_sel_action)

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        # self.status_left_lbl = QLabel('statusbar left')
        # self.statusbar.addPermanentWidget(self.status_left_lbl, 1)

        self.statusbar_right_lbl = QLabel('')
        self.statusbar.insertPermanentWidget(1, self.statusbar_right_lbl)

        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_start_measure.setText(_translate("MainWindow", "Start measure"))
        self.btn_start_measure.setStatusTip(_translate("MainWindow", "Start the measurements"))
        self.btn_stop_measure.setText(_translate("MainWindow", "Stop measure"))
        self.saveAction.setStatusTip(_translate("MainWindow", "Save into CSV file"))
        self.saveAction.setStatusTip(_translate("MainWindow", "Open from CSV file"))
        # self.label1.setText(_translate("MainWindow", "TextLabel"))
        # self.btnStopMeasure.setText(_translate("MainWindow", "PushButton"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
