import sys
# import pyximport; pyximport.install()

from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from MainWindow import Ui_MainWindow

import traceback, sys
import serial
import time
import sys
import time

import numpy as np

import views
import data
import pandas as pd
import protocols
import measurements

import threading

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.nsamp = 12000
        self.nch = 6
        self.fs = 100
        view_ranges = [1000, 3000, 6000, 12000]
        self.nsamp_view = view_ranges[2]

        self.data_cntrl = data.DataController(self.nch, self.nsamp, self.fs)

        self.central_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.plot_widget = views.COPView(self.x, self.data_cntrl.meas_data.y_raw, self.data_cntrl, self.nsamp_view)
        self.cop_plot_settings = []
        # self.liveplot_view = views.LivePlotView(self.x, self.y)
        self.central_layout.addWidget(self.plot_widget)
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.plot_widget)

        self.saveAction.triggered.connect(self.save_data_csv)
        self.openAction.triggered.connect(self.open_data_csv)

        self.btn_start_measure.triggered.connect(self.start_measure)
        # self.btn_start_measure.setCheckable(True)
        self.btn_stop_measure.triggered.connect(self.stop_measure)

        self.btn_show_liveplot.triggered.connect(lambda: self.set_central_widget(self.btn_show_liveplot))
        self.btn_show_copplot.triggered.connect(lambda: self.set_central_widget(self.btn_show_copplot))

        # self.btn = QPushButton("Liveplot")

        self.timer = QTimer()

        port = 'COM8'
        baudrate = 115200

        self.run = False
        self.ref_rate = 10

        self.meas_cntrl = measurements.MesurementController(self.data_cntrl, port, baudrate)

        for i, vrange in enumerate(view_ranges):
            nsec = vrange // self.fs
            if nsec >= 60:
                vrange_format = f'{int(nsec/60)} min'
            else:
               vrange_format = f'{nsec} sec'
            action = QAction(vrange_format)
            action.setData(vrange)
            action.setCheckable(True)
            self.samp_range_view_menu.addAction(action)
            self.samp_range_view_group.addAction(action)
            if vrange == self.nsamp_view:
                action.setChecked(True)
        self.samp_range_view_group.triggered.connect(lambda action: self.set_view_range(int(action.data())))

        refresh_rates = ['1', '5', '10']
        for i, refrate in enumerate(refresh_rates):
            action = QAction(refrate+' Hz')
            action.setCheckable(True)
            self.refresh_view_menu.addAction(action)
            self.refresh_view_group.addAction(action)
            if refrate == '10':
                action.setChecked(True)
        self.refresh_view_group.triggered.connect(lambda action: self.set_refresh_rate(int(action.text()[:-3])))

        self.autoscale_view = True
        self.autscale_action.setCheckable(self.autoscale_view)
        self.autscale_action.setChecked(self.autoscale_view)
        self.plot_widget.set_autoscale(self.autoscale_view)
        self.autscale_action.triggered.connect(self.set_autoscale_view)

        self.meas_time_timer = QTimer(self)
        self.meas_time_timer.timeout.connect(self.update_meas_time)
        self.meas_start_time = QTime.currentTime()
        self.update_meas_time()

    def set_central_widget(self, btn):
        if btn is self.btn_show_liveplot:
            new_widget = views.LivePlotView(*self.data_cntrl.get_meas(self.nsamp_view), self.data_cntrl, self.nsamp_view)
            self.cop_plot_settings = self.plot_widget.get_settings()
        elif btn is self.btn_show_copplot:
            new_widget = views.COPView(*self.data_cntrl.get_meas(self.nsamp_view), self.data_cntrl, self.nsamp_view)
            new_widget.update_canvas()
            new_widget.set_settings(self.cop_plot_settings)
        # self.central_layout.removeWidget(self.plot_widget)
        # self.central_layout.insertWidget(0, self.plot_widget)
        # self.central_layout.update()
        if self.run:
            self.timer.timeout.connect(new_widget.update_canvas)
        else:
            new_widget.update_canvas()
            new_widget.show_slider(0, self.data_cntrl.cnt)
            new_widget.show_slider(0, self.data_cntrl.cnt)
            # print(self.plot_widget.get_view_range())
            new_widget.slider.setRange(*self.plot_widget.get_view_range())
            # new_widget.slider.repaint()
        # self.plot_widget.close()
        self.plot_widget = new_widget
        self.plot_widget.set_autoscale(self.autoscale_view)
        self.autscale_action.triggered.connect(self.set_autoscale_view)
        self.setCentralWidget(self.plot_widget)
        # self.plot_widget = new_widget
        # if self.run:
        #     self.timer.timeout.connect(self.plot_widget.update_canvas)
        # else:
        #     self.plot_widget.update_canvas()

        # self.setCentralWidget(self.central_widget)
        # self.timer.start(100)

    def set_autoscale_view(self, val):
        self.autoscale_view = val
        self.plot_widget.set_autoscale(self.autoscale_view)

    def set_view_range(self, nsamp):
        self.nsamp_view = nsamp
        self.plot_widget.nsamp_view = nsamp

    def set_refresh_rate(self, refrate):
        print(refrate)
        self.ref_rate = refrate
        if self.run:
            self.timer.setInterval(1000 / self.ref_rate)

    def set_port(self, port):
        self.meas_cntrl.set_port(port)

    def start_measure(self):
        self.data_cntrl.clear_data()
        self.run = True
        self.meas_cntrl.connect()
        # self.serial_thread = threading.Thread(target=self.makeMeasurements)
        self.plot_widget.hide_slider()
        self.timer.timeout.connect(self.plot_widget.update_canvas)
        # Execute
        # self.serial_thread.start()
        self.meas_cntrl.start_measure()
        self.timer.start(int(1000 / self.ref_rate))
        self.meas_time_timer.start(1000)
        self.meas_start_time = QTime.currentTime()
        self.setWindowTitle('Making measurements')
        # self.central_widget.startUpdating()

    def stop_measure(self):
        self.run = False
        self.timer.timeout.disconnect(self.plot_widget.update_canvas)
        self.timer.stop()
        self.meas_time_timer.stop()
        # try:
        self.meas_cntrl.stop_measure()
        self.data_cntrl.concatenate_data()
        self.plot_widget.show_slider(0, self.data_cntrl.cnt)
        self.plot_widget.update_canvas()
        # except:
        #     pass

    def save_data_csv(self):
        fpath = QFileDialog.getSaveFileName(self, 'Save File', '', "CSV files (*.csv)")[0]
        if fpath is not '':
            df = self.data_cntrl.to_dataframe()
            df.to_csv(fpath, float_format='%g')

    def open_data_csv(self):
        fpath = QFileDialog.getOpenFileName(self, 'Open File', '', "CSV files (*.csv)")[0]
        if fpath is not '':
            self.setWindowTitle(fpath)
            df = pd.read_csv(fpath)
            self.data_cntrl.from_dataframe(df)
            self.plot_widget.update_canvas()
            self.plot_widget.show_slider(0, self.data_cntrl.cnt)

    def update_meas_time(self):
        seconds = self.meas_start_time.secsTo(QTime.currentTime())
        time = QTime().fromMSecsSinceStartOfDay(1000*seconds)
        # text = str(time) #time.toString('mm:ss')
        text = time.toString('mm:ss')
        self.measure_time_label.setText(text)
        # self.measure_time_label.display(text)

    # def closeEvent(self, event):
    #     self.run = False
    #     try:
    #         self.central_widget.close()
    #     except:
    #         pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())