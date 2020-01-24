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
import widgets
import protocols

import threading

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.threadpool = QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.nsamp = 12000
        self.nch = 6
        self.fs = 100
        # self.t_data = data.TimesData()
        # self.meas_data = data.MeasurementsData(nch)
        # self.cop_data = data.CopData(nsamp)

        # self.t_data = data.TimesData(self.nsamp)
        # self.meas_data = data.MeasurementsData(self.nch, self.nsamp)
        # self.cop_data = data.CopData(self.nsamp)

        self.data_cntrl = data.DataController(self.nch, self.nsamp, self.fs)

        self.central_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.plot_widget = views.COPView(self.x, self.data_cntrl.meas_data.y_raw, self.data_cntrl)
        self.cop_plot_settings = []
        # self.liveplot_view = views.LivePlotView(self.x, self.y)
        self.central_layout.addWidget(self.plot_widget)
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.plot_widget)

        self.saveAction.triggered.connect(self.save_data_csv)
        self.openAction.triggered.connect(self.open_data_csv)

        self.btn_start_measure.triggered.connect(self.startMeasure)
        # self.btn_start_measure.setCheckable(True)
        self.btn_stop_measure.triggered.connect(self.stopMeasure)

        self.btn_show_liveplot.triggered.connect(lambda: self.set_central_widget(self.btn_show_liveplot))
        self.btn_show_copplot.triggered.connect(lambda: self.set_central_widget(self.btn_show_copplot))

        # self.btn = QPushButton("Liveplot")

        self.timer = QTimer()
        # static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # layout.addWidget(static_canvas)
        # self.addToolBar(NavigationToolbar(static_canvas, self))

        self.ser = None
        self.port = None
        self.is_conn = False
        self.search_connection()



        self.run = False
        self.cnt = 0
        self.nsamp_view = 0
        self.show_every = 1
        self.ref_rate = 10

        view_ranges = [1000, 3000, 6000, 12000]
        self.nsamp_view_max = view_ranges[2]
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
            if vrange == self.nsamp_view_max:
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
        self.meas_time_timer.timeout.connect(self.showTime)
        self.meas_start_time = QTime.currentTime()
        self.showTime()

    def set_central_widget(self, btn):
        if btn is self.btn_show_liveplot:
            new_widget = views.LivePlotView(*self.data_cntrl.get_meas(), self.data_cntrl)
            self.cop_plot_settings = self.plot_widget.get_settings()
        elif btn is self.btn_show_copplot:
            new_widget = views.COPView(*self.getDataRaw(), self)
            new_widget.update_canvas()
            new_widget.set_settings(self.cop_plot_settings)
        # self.central_layout.removeWidget(self.plot_widget)
        # self.central_layout.insertWidget(0, self.plot_widget)
        # self.central_layout.update()
        if self.run:
            self.timer.timeout.connect(new_widget.update_canvas)
        else:
            new_widget.update_canvas()
            new_widget.show_slider(0, self.cnt)
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
        self.nsamp_view_max = nsamp

    def set_refresh_rate(self, refrate):
        print(refrate)
        self.ref_rate = refrate
        if self.run:
            self.timer.setInterval(1000 / self.ref_rate)



    def search_connection(self):
        port_list = protocols.get_ports_list()
        if len(port_list) == 1:
            self.port = port_list[0]
            self.is_conn = self.try_connect()
        elif len(port_list) > 1:
            for port in port_list:
                self.port = port
                self.is_conn = self.try_connect()
                if self.is_conn:
                    break
        else:
            self.port = None

        if self.is_conn:
            self.ser.close()

        for act in self.port_act_group.actions():
            self.port_act_group.removeAction(act)
            self.port_sel_menu.removeAction(act)

        for port in port_list:
            action = QAction(port)
            action.setCheckable(True)
            self.port_sel_menu.addAction(action)
            self.port_act_group.addAction(action)
            if port == self.port:
                action.setChecked(True)
            # action.triggered.connect(lambda item=action.text(): self.set_port(action.text()))
        self.port_act_group.triggered.connect(lambda action: self.set_port(action.text()))

        # if self.port is not None:

    def try_connect(self):
        result = False
        if self.port is not None:
            try:
                self.ser = serial.Serial(self.port, 115200)  # COM4
                self.statusbar_right_lbl.setText(self.ser.portstr)
                result = True
            except serial.SerialException as e:
                self.statusbar_right_lbl.setText(str(e).split(':')[0])
        else:
            self.statusbar_right_lbl.setText('no ports available')
            print('no ports available')
        print('result', result)
        return result

    def set_port(self, port):
        print(port)
        self.port = port
        self.is_conn = self.try_connect()

    def startMeasure(self):
        print(self.port, self.is_conn)
        if not self.is_conn:
            self.search_connection()

        self.is_conn = self.try_connect()
        print(self.port, self.is_conn)

        if not self.is_conn:
            return

        self.y_raw = []
        self.y_trans = []
        self.xy_cop = []
        self.times = []
        self.cnt = 0
        self.nsamp_view = 0
        self.data_cntrl.t_data = data.TimesData(self.nsamp)
        self.data_cntrl.meas_data = data.MeasurementsData(self.nch, self.nsamp)
        self.data_cntrl.cop_data = data.CopData(self.nsamp)
        self.run = True
        worker = Worker(self.makeMeasurements)  # Any other args, kwargs are passed to the run function
        # self.serial_thread = threading.Thread(target=self.makeMeasurements)
        self.plot_widget.hide_slider()
        self.timer.timeout.connect(self.plot_widget.update_canvas)
        # Execute
        # self.serial_thread.start()
        self.threadpool.start(worker)
        self.timer.start(1000 / self.ref_rate)
        self.meas_time_timer.start(1000)
        self.setWindowTitle('Making measurements')
        # self.central_widget.startUpdating()

    def makeMeasurements(self):
        import serial
        nch = 6

        # x = np.linspace(0, nsamp_view, nsamp_view + 1)[0:-1]
        self.meas_start_time = QTime.currentTime()
        # set up the serial line
        self.ser.flushInput()
        # time.sleep(2)
        self.ser.readline()
        while self.run:
            ''' Read and add '''
            b = self.ser.readline()  # read a byte string
            sep = b.split()
            samples = np.array([int(s) for s in sep], dtype=np.uint16)
            # print(samples)
            if len(sep) == nch:
                self.cnt += 1
                if self.cnt > self.nsamp_view_max:
                    self.nsamp_view = self.nsamp_view_max
                else:
                    self.nsamp_view = self.cnt - 1
                self.data_cntrl.t_data.append(self.cnt * 1000 / self.fs)
                self.data_cntrl.meas_data.append(samples)
                self.data_cntrl.cop_data.append(self.data_cntrl.meas_data)
                if self.cnt % self.nsamp == 0:
                    self.append_chunk_data()
            else:
                print('!', samples)
                self.ser.flushInput()

    def append_chunk_data(self):
        self.y_raw.append(self.data_cntrl.meas_data.y_raw)
        self.y_trans.append(self.data_cntrl.meas_data.y_trans)
        self.times.append(self.data_cntrl.t_data.t)
        self.xy_cop.append(self.data_cntrl.cop_data.xyc)

    def concatenate_data(self):
        split = - (self.cnt % self.nsamp)
        self.y_raw.append(self.data_cntrl.meas_data.y_raw[:, split:])
        self.y_trans.append(self.data_cntrl.meas_data.y_trans[:, split:])
        self.times.append(self.data_cntrl.t_data.t[split:])
        self.xy_cop.append(self.data_cntrl.cop_data.xyc[:, split:])
        self.y_raw = np.concatenate(self.y_raw, axis=1)
        self.y_trans = np.concatenate(self.y_trans, axis=1)
        self.xy_cop = np.concatenate(self.xy_cop, axis=1)
        self.times = np.concatenate(self.times)

    def save_data_csv(self):
        fpath = QFileDialog.getSaveFileName(self, 'Save File', '', "CSV files (*.csv)")[0]
        if fpath is not '':
            df_times = pd.DataFrame()
            df_times['sample'] = self.times
            # df_times[['0', '1', '2', '3', '4', '5']] = self.y_raw.T
            df_y_raw = pd.DataFrame.from_records(self.y_raw.T, columns=['raw_'+str(i) for i in range(self.nch)])
            print(np.shape(self.y_raw))
            df_y_trans = pd.DataFrame.from_records(self.y_trans.T, columns=['press_'+str(i) for i in range(self.nch)])
            df_cop = pd.DataFrame.from_records(self.xy_cop.T, columns=['cop_x_r', 'cop_y_r', 'cop_x_l', 'cop_x_r',
                                                                             'cop_x_all', 'cop_y_all'])
            df = pd.concat([df_times, df_y_raw, df_y_trans, df_cop], axis=1, sort=False)
            df.to_csv(fpath, float_format='%g')

    def open_data_csv(self):
        fpath = QFileDialog.getOpenFileName(self, 'Open File', '', "CSV files (*.csv)")[0]
        if fpath is not '':
            self.setWindowTitle(fpath)
            df = pd.read_csv(fpath)
            self.times = df['sample'].to_numpy()
            self.y_raw = df[['raw_'+str(i) for i in range(self.nch)]].to_numpy().T
            self.y_trans = df[['press_'+str(i) for i in range(self.nch)]].to_numpy().T
            self.xy_cop = df[['cop_x_r', 'cop_y_r', 'cop_x_l', 'cop_x_r', 'cop_x_all', 'cop_y_all']].to_numpy().T
            # print(np.shape(self.y_raw))
            self.cnt = len(self.times)
            self.plot_widget.update_canvas()
            self.plot_widget.show_slider(0, self.cnt)

    def stopMeasure(self):
        self.timer.timeout.disconnect(self.plot_widget.update_canvas)
        self.timer.stop()
        self.meas_time_timer.stop()
        self.run = False
        try:
            self.ser.close()
            self.concatenate_data()
            self.plot_widget.show_slider(0, self.cnt)
            self.plot_widget.update_canvas()
        except:
            pass

    def showTime(self):
        seconds = self.meas_start_time.secsTo(QTime.currentTime())
        time = QTime().fromMSecsSinceStartOfDay(1000*seconds)
        # text = str(time) #time.toString('mm:ss')
        text = time.toString('mm:ss')
        self.measure_time_label.setText(text)
        # self.measure_time_label.display(text)

    def closeEvent(self, event):
        self.run = False
        try:
            self.central_widget.close()
        except:
            pass

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
        #     exctype, value = sys.exc_info()[:2]
        #     self.signals.error.emit((exctype, value, traceback.format_exc()))
        # else:
        #     self.signals.result.emit(result)  # Return the result of the processing
        # finally:
        #     self.signals.finished.emit()  # Done

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())