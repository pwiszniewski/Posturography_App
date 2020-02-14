from PySide2.QtCore import *
import serial
import numpy as np

class MesurementController():
    def __init__(self, data_cntrl, port=None, baudrate=None):
        self.data_cntrl = data_cntrl
        self.port = port
        self.baudrate = baudrate
        self.meas_worker = None
        self.threadpool = QThreadPool()

    def set_port(self, port):
        self.port = port

    def connect(self):
        self.meas_worker = MeasurementWorker(self.data_cntrl, self.port, self.baudrate)

    def start_measure(self):
        # if not self.is_conn:
        #     self.search_connection()

        # self.is_conn = self.try_connect()
        # print(self.port, self.is_conn)

        # if not self.is_conn:
        #     return
        self.threadpool.start(self.meas_worker)

    def stop_measure(self):
        self.meas_worker.stop()


class MeasurementWorker(QRunnable):
    def __init__(self, data_cntrl, port, baud_rate, *args, **kwargs):
        super(MeasurementWorker, self).__init__()
        self.data_cntrl = data_cntrl
        self.port = port
        self.ser = serial.Serial(self.port, baud_rate)
        self.is_run = False
        # # Store constructor arguments (re-used for processing)
        # self.fn = fn
        # self.args = args
        # self.kwargs = kwargs

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        self.ser.flushInput()
        self.ser.readline()
        self.is_run = True
        while self.is_run:
            ''' Read and add '''
            b = self.ser.readline()  # read a byte string
            sep = b.split()
            samples = np.array([int(s) for s in sep], dtype=np.uint16)
            # print(samples)
            if len(sep) == self.data_cntrl.nchann:
                # self.cnt += 1
                # if self.cnt > self.nsamp_view_max:
                #     self.nsamp_view = self.nsamp_view_max
                # else:
                #     self.nsamp_view = self.cnt - 1
                self.data_cntrl.append_meas(samples)
            else:
                print('!', samples)
                self.ser.flushInput()

    def stop(self):
        self.is_run = False
        self.ser.close()