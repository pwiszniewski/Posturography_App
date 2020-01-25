from dataclasses import dataclass
import numpy as np


class DataController:
    def __init__(self, nchann, nsamp, fs):
        self.t_data = TimesData(nsamp)
        self.meas_data = MeasurementsData(nchann, nsamp)
        self.cop_data = CopData(nsamp)
        self.fs = fs
        self.cnt = 0
        self.nsamp = nsamp
        self.nchann = nchann
        self.concat = False

        self.y_raw = []
        self.y_trans = []
        self.xy_cop = []
        self.times = []

    def append_meas(self, samples):
        self.cnt += 1
        self.t_data.append(self.cnt * 1000 / self.fs)
        self.meas_data.append(samples)
        self.cop_data.append(self.meas_data)

        if self.cnt % self.nsamp == 0:
            self.append_chunk_data()

    def append_chunk_data(self):
        print('append_chunk_data')
        self.y_raw.append(self.meas_data.y_raw)
        self.y_trans.append(self.meas_data.y_trans)
        self.times.append(self.t_data.t)
        self.xy_cop.append(self.cop_data.xyc)

    def concatenate_data(self):
        print('concatenate_data')
        split = - (self.cnt % self.nsamp)
        self.y_raw.append(self.meas_data.y_raw[:, split:])
        self.y_trans.append(self.meas_data.y_trans[:, split:])
        self.times.append(self.t_data.t[split:])
        self.xy_cop.append(self.cop_data.xyc[:, split:])
        self.y_raw = np.concatenate(self.y_raw, axis=1)
        self.y_trans = np.concatenate(self.y_trans, axis=1)
        self.xy_cop = np.concatenate(self.xy_cop, axis=1)
        self.times = np.concatenate(self.times)
        self.concat = True

    def clear_data(self):
        self.y_raw = []
        self.y_trans = []
        self.xy_cop = []
        self.times = []
        self.cnt = 0
        self.t_data = TimesData(self.nsamp)
        self.meas_data = MeasurementsData(self.nchann, self.nsamp)
        self.cop_data = CopData(self.nsamp)
        self.concat = False

    def get_meas(self):
        if not self.concat:
            return self.t_data.t[-self.cnt:], self.meas_data.y_trans[:, -self.cnt:]
        else:
            return self.times, self.y_trans
        # print('getdata')
        # if self.run:
        #     return self.t_data.t[-nsamp:-1], self.meas_data.y_trans[:, -nsamp:-1]


    def get_meas_raw(self):
        # print('getDataRaw')
        if self.run:
            return self.data_cntrl.t_data.t[-nsamp:-1], self.meas_data.y_raw[:, -nsamp:-1]
        else:
            return self.times, self.y_raw

    def get_cop(self):
        return self.cop_data.xyc[:, -self.cnt:]
        # if self.run:
        #     return self.cop_data.xyc[:, -nsamp:]
        # else:
        #     return self.xy_cop

    def get_times(self, nsamp):
        if self.run:
            return self.t_data.t[-nsamp:-1]
        else:
            return self.times

    # def get_meas(self):
    #     return self.meas_data.y_trans
    #
    # def get_meas_raw(self):
    #     return self.meas_data.y_raw
    #
    # def get_times(self):
    #     return self.t_data.t

# @dataclass
# class MeasurementsData:
#     def __init__(self, nch, max_nsamp=None):
#         self.nch = nch
#         self.nsamp = 0
#         self.max_nsamp = max_nsamp
#         self.y_raw = np.zeros((nch, max_nsamp), dtype=np.uint16)
#         self.y_trans = np.zeros((nch, max_nsamp))
#         self.sum_all = 500
#
#     def append(self, samples):
#         R20kg = 10
#         R50kg = 47
#         R = np.array([R50kg, R20kg, R20kg, R50kg, R20kg, R20kg])
#         Uwe = 1023
#         a20kg = 267.5
#         a50kg = 684.9
#         a = np.array([a50kg, a20kg, a20kg, a50kg, a20kg, a20kg])
#
#         for i in range(self.nch):
#             lastsamp = samples[i]
#             self.y_raw[i, -1] = lastsamp
#             self.y_trans[i, -1] = a[i] / (R[i] * (lastsamp + 1e-6) / (Uwe - lastsamp + 1e-6))
#
#         # self.y_raw = np.roll(self.y_raw, -1)
#         # self.y_trans = np.roll(self.y_trans, -1)
#         # self.y_raw[:, -1] = samples
#         # self.y_trans[:, -1] = a / (R * (samples + 1e-6) / (Uwe - samples + 1e-6))

@dataclass
class MeasurementsData:
    def __init__(self, nch, max_nsamp=None):
        self.nch = nch
        self.nsamp = 0
        self.max_nsamp = max_nsamp
        self.y_raw = np.zeros((nch, max_nsamp), dtype=np.uint16)
        self.y_trans = np.zeros((nch, max_nsamp))
        self.sum_all = 0
    # nch = 6
    # nsamp = 10_000
    # n = 0
    # sum_all = 0
    # y_raw: np.ndarray = np.zeros((nch, nsamp), dtype=np.uint16)
    # y_trans: np.ndarray = np.zeros((nch, nsamp))
    #
    # def __init__(self, nch, max_nsamp=None):
    #     self.nch = nch

    def append(self, samples):
        R20kg = 10
        R50kg = 47
        R = [R50kg, R20kg, R20kg, R50kg, R20kg, R20kg]
        Uwe = 1023
        a20kg = 267.5
        a50kg = 684.9
        a = [a50kg, a20kg, a20kg, a50kg, a20kg, a20kg]

        self.y_raw = np.roll(self.y_raw, -1)
        self.y_trans = np.roll(self.y_trans, -1)

        self.sum_all = 0

        for i in range(self.nch):
            lastsamp = int(samples[i])
            self.y_raw[i, -1] = lastsamp
            self.y_trans[i, -1] = a[i] / (R[i] * (lastsamp + 1e-6) / (Uwe - lastsamp + 1e-6))
            self.sum_all += self.y_trans[i, -1]

@dataclass
class CopData:
    def __init__(self, max_nsamp=None):
        self.max_nsamp = max_nsamp
        self.xyc = np.zeros((6, max_nsamp))
    def append(self, meas_data):
        # self.sum_all = 0
        # for i in range(self.nch):
        #     lastsamp = int(samples[i])
        #     self.sum_all += self.y_trans[i, -1]

        nx_P, ny_P, nx_L, ny_L, nx_all, ny_all = 0, 1, 2, 3, 4, 5
        y = meas_data.y_trans
        sum_all = meas_data.sum_all
        self.xyc = np.roll(self.xyc, -1)
        sum_P = sum(y[:2, -1])
        sum_L = sum(y[2:5, -1])
        self.xyc[nx_P, -1] = (0.3 * y[0, -1] + 2.3 * y[1, -1] - 2.8 * y[2, -1]) / sum_P
        self.xyc[ny_P, -1] = (-7.1 * y[0, -1] + 6.3 * y[1, -1] + 8 * y[2, -1]) / sum_P
        self.xyc[nx_L, -1] = (-0.3 * y[3, -1] - 2.3 * y[4, -1] + 2.8 * y[5, -1]) / sum_L
        self.xyc[ny_L, -1] = (-7.1 * y[3, -1] + 6.3 * y[4, -1] + 8 * y[5, -1]) / sum_L
        self.xyc[nx_all, -1] = (8.7 * y[0, -1] + 10 * y[1, -1] + 5.1 * y[2, -1]
                           - 8.3 * y[3, -1] - 10 * y[4, -1] - 5.3 * y[5, -1]) / sum_all
        self.xyc[ny_all, -1] = (-10.5 * y[0, -1] + 2.55 * y[1, -1] + 4 * y[2, -1]
                           - 11 * y[3, -1] + 2.4 * y[4, -1] + 4 * y[5, -1]) / sum_all + 7.5


@dataclass
class TimesData:
    def __init__(self, max_nsamp=None):
        self.max_nsamp = max_nsamp
        if max_nsamp is not None:
            self.t = np.zeros(max_nsamp)
        else:
            # self.t = []
            self.t = np.zeros(0)

    def append(self, t):
        if self.max_nsamp is not None:
            self.t = np.roll(self.t, -1)
            self.t[-1] = t
        else:
            self.t = np.append(self.t, t)