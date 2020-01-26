from PySide2.QtWidgets import *
from PySide2 import QtCore
import plots
import numpy as np

import widgets

import matplotlib
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
import matplotlib.pyplot as plt
import time
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT)
from matplotlib.figure import Figure
from matplotlib import backend_bases
# mpl.rcParams['toolbar'] = 'None'

class NavigationToolbar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] is not 'Subplots']

class LivePlotView(QWidget):
    def __init__(self, x, y, data_obj, nsamp_view, autoscale=False, *args, **kwargs):
        super(LivePlotView, self).__init__(*args, **kwargs)

        self.data_obj = data_obj
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # layout = self.layout()
        layout = QVBoxLayout()
        self.toolbar = NavigationToolbar(dynamic_canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(dynamic_canvas)

        # self.setCentralWidget(dynamic_canvas)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                 NavigationToolbar(dynamic_canvas, self))
        self.setLayout(layout)

        self.fig = dynamic_canvas.figure
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        # self._timer = dynamic_canvas.new_timer(
        #     100, [(self._update_canvas, (), {})])

        formatter = matplotlib.ticker.FuncFormatter(lambda ms, x: time.strftime('%M:%S', time.gmtime(ms // 1000)))
        self._dynamic_ax.xaxis.set_major_formatter(formatter)

        nch = 6
        self.xyc = []
        self.x = x
        self.y = y

        chnames = ['P|PIĘTA', 'P|ZEW', 'P|WEW', 'L|PIĘTA', 'L|ZEW', 'L|WEW']
        colors = ['#e866c5', 'g', 'b', '#d466e8', 'orange', '#fff740']
        self.nsamp_view = nsamp_view
        self.y_lim = (0, 50)
        self.autoscale = autoscale
        self.plot = plots.LivePlot(self._dynamic_ax, self.x, self.y, nch, self.y_lim, colors, chnames, self.autoscale)

        self.slider = widgets.QRangeSlider()
        self.slider.setFixedHeight(36)
        self.slider.startValueChanged.connect(self.set_x_min_view)
        self.slider.endValueChanged.connect(self.set_x_max_view)
        self.layout().addWidget(self.slider)
        self.slider.setHidden(True)

    def set_x_min_view(self, x_min):
        self.x_min = x_min
        self.update_view_range()

    def set_x_max_view(self, x_max):
        self.x_max = x_max
        self.update_view_range()

    def update_view_range(self):
        self.plot.set_data(self.x[self.x_min:self.x_max], self.y[:, self.x_min:self.x_max])
        self.plot.update()
        self.fig.canvas.draw()

    def get_view_range(self):
        return self.x_min, self.x_max

    def update_canvas(self):
        self.x, self.y = self.data_obj.get_meas(self.nsamp_view)
        # print(self.x[:3], self.y[0, :3])
        self.fig.axes.clear()
        # self.fig.canvas.draw()
        self.plot.set_data(self.x, self.y)
        self.plot.update()
        self.fig.canvas.draw()

    def show_slider(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max
        self.slider.setMin(x_min)
        self.slider.setMax(x_max)
        self.slider.setRange(x_min, x_max)
        # self.slider.update()
        self.slider.setHidden(False)

    def hide_slider(self):
        self.slider.setHidden(True)

    def set_autoscale(self, val):
        self.autoscale = val
        self.plot.set_autoscale(val)
        if not self.autoscale:
            self.plot.set_y_lim(self.y_lim)
        try:
            self.update_view_range()
        except:
            self.update_canvas()

    # def startUpdating(self):
    #     self._timer.start()
    #     print('startUpdating')


class COPView(QWidget):
    def __init__(self, x, y, data_obj, nsamp_view, autoscale=False, *args, **kwargs):
        super(COPView, self).__init__(*args, **kwargs)

        self.data_obj = data_obj
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # layout = self.layout()
        layout = QVBoxLayout()
        self.toolbar = NavigationToolbar(dynamic_canvas, self)
        # layout.addWidget(self.toolbar)
        # layout.addWidget(btnStopMeasure)

        chbox_layout = QHBoxLayout()
        chbox_layout.addWidget(self.toolbar)
        self.b1 = QCheckBox("Point")
        chbox_layout.addWidget(self.b1)
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda: self.btnstate(self.b1))

        self.b2 = QCheckBox("Show all points")
        chbox_layout.addWidget(self.b2)
        self.b2.setChecked(False)
        self.b2.toggled.connect(lambda: self.btnstate(self.b2))

        self.b3 = QCheckBox("Histogram")
        chbox_layout.addWidget(self.b3)
        self.b3.setChecked(True)
        self.b3.toggled.connect(lambda: self.btnstate(self.b3))

        self.b4 = QCheckBox("Curve")
        chbox_layout.addWidget(self.b4)
        self.b4.setChecked(True)
        self.b4.toggled.connect(lambda: self.btnstate(self.b4))

        self.b5 = QCheckBox("Dark")
        chbox_layout.addWidget(self.b5)
        # self.b5.setChecked(True)
        self.b5.toggled.connect(lambda: self.btnstate(self.b5))

        layout.addLayout(chbox_layout)
        # self.btnClear.clicked.connect(self.clear)
        layout.addWidget(dynamic_canvas)
        # self.setCentralWidget(dynamic_canvas)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                 NavigationToolbar(dynamic_canvas, self))
        self.setLayout(layout)
        # self._ax_COP_global = dynamic_canvas.figure.add_subplot(1, 2, 1)
        # self._ax_COP_left = dynamic_canvas.figure.add_subplot(1, 4, 3)
        # self._ax_COP_right = dynamic_canvas.figure.add_subplot(1, 4, 4)
        # self._ax_color_bar = dynamic_canvas.figure.add_axes([0.93, 0.11, 0.02, 0.77])

        # gs = dynamic_canvas.figure.add_gridspec(1, 20)
        # self._ax_COP_global = dynamic_canvas.figure.add_subplot(gs[0, 0:10])
        # self._ax_COP_left = dynamic_canvas.figure.add_subplot(gs[0, 10:14])
        # self._ax_COP_right = dynamic_canvas.figure.add_subplot(gs[0, 14:18])
        # self._ax_color_bar = dynamic_canvas.figure.add_subplot(gs[0, 18])
        #
        #
        # self._ax_COP_left.margins(0.5, 0.5)
        # dynamic_canvas.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, hspace=0, wspace=0.1)

        bottom = 0.1
        height = 0.85
        width = 0.15  # * 4 = 0.6 - minus the 0.1 padding 0.3 left for space
        left1, left2, left3, left4 = 0.05, 0.5, 1 - 0.25 - width, 1 - 0.05 - width
        height_bar = 0.03
        bottom_bar = 1-(bottom+height+height_bar)+0.01

        show_bars = True
        if show_bars:
            # rectangle1 = [0.05, bottom, 0.45, height]
            # rectangle2 = [0.53, bottom, 0.2, height]
            # rectangle3 = [0.74, bottom, 0.2, height]
            # rectangle4 = [0.96, bottom, 0.01, height]
            # rectangle1 = [0.03, bottom, 0.45, height]
            # rectangle2 = [0.51, bottom, 0.2, height]
            # rectangle3 = [0.74, bottom, 0.2, height]
            # rectangle4 = [0.88, bottom, 0.01, height]
            # rectangle5 = [0.92, bottom, 0.01, height]
            # rectangle6 = [0.96, bottom, 0.01, height]
            rectangle1 = [0.03, bottom, 0.45, height]
            rectangle2 = [0.53, bottom, 0.21, height]
            rectangle3 = [0.77, bottom, 0.21, height]
            rectangle4 = [0.03, bottom_bar, 0.45, height_bar]
            rectangle5 = [0.53, bottom_bar, 0.21, height_bar]
            rectangle6 = [0.77, bottom_bar, 0.21, height_bar]
        else:
            rectangle1 = [0.05, bottom, 0.45, height]
            rectangle2 = [0.53, bottom, 0.21, height]
            rectangle3 = [0.77, bottom, 0.21, height]

        self.fig = dynamic_canvas.figure
        self._ax_COP_global = self.fig.add_axes(rectangle1)
        self._ax_COP_left = self.fig.add_axes(rectangle2)
        self._ax_COP_right = self.fig.add_axes(rectangle3)

        if show_bars:
            self._ax_color_bar_g = self.fig.add_axes(rectangle4)
            self._ax_color_bar_l = self.fig.add_axes(rectangle5)
            self._ax_color_bar_r = self.fig.add_axes(rectangle6)
        else:
            self._ax_color_bar_g = None
            self._ax_color_bar_l = None
            self._ax_color_bar_r = None

        # self._ax_COP_right.set_yticklabels([])

        # self._timer = dynamic_canvas.new_timer(
        #     100, [(self._update_canvas, (), {})])

        nch = 6
        self.xy_cop = []
        self.x = x
        self.y = y

        self.nsamp_view = nsamp_view

        hist_size_lr = [9, 9]
        x_min_lr, x_max_lr = -10, 10
        y_min_lr, y_max_lr = -10, 10
        y_hist_offset_lr = 0 #-20
        self.x_lim_lr, self.y_lim_lr = (x_min_lr, x_max_lr), (y_min_lr, y_max_lr)

        hist_size_g = [19, 19]
        x_hist_min_g, x_hist_max_g = -10, 10 #0, 1024
        y_hist_min_g, y_hist_max_g = -10, 10
        y_hist_offset_g = 0 #5
        self.x_lim_g, self.y_lim_g = (x_hist_min_g, x_hist_max_g), (y_hist_min_g, y_hist_max_g)

        # self._point_global = plots.PointPlot(self._ax_COP_global, 0, 0, x_hist_range, y_hist_range)
        # self._point_left = plots.PointPlot(self._ax_COP_left, 0, 0, x_hist_range, y_hist_range)
        # self._point_right = plots.PointPlot(self._ax_COP_right, 0, 0, x_hist_range, y_hist_range)
        self.autoscale = autoscale
        nsamp = 10_000
        y = np.zeros((nch, nsamp))
        self.plot_COP_global = plots.CombinedPointCurveHistogramPlot(self._ax_COP_global, y[0], y[1], self.x_lim_g, self.y_lim_g,
                                                                    hist_size_g, y_hist_offset_g, show_bar=show_bars,
                                                                     bar_ax=self._ax_color_bar_g, title='COP', autoscale=self.autoscale)
        self.plot_COP_left = plots.CombinedPointCurveHistogramPlot(self._ax_COP_left, y[0], y[0], self.x_lim_lr, self.y_lim_lr, hist_size_lr,
                                                                   y_hist_offset_lr, show_bar=show_bars, bar_ax=self._ax_color_bar_l,
                                                                   title='COP left', autoscale=self.autoscale)
        self.plot_COP_right = plots.CombinedPointCurveHistogramPlot(self._ax_COP_right, y[0], y[0], self.x_lim_lr, self.y_lim_lr, hist_size_lr,
                                                               y_hist_offset_lr, show_bar=show_bars, bar_ax=self._ax_color_bar_r,
                                                                    title='COP right', autoscale=self.autoscale)
        self.fig.canvas.draw()
        # self.slider.setDrawValues(False)
        # self.slider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        # self.slider.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')

        self.slider = widgets.QRangeSlider()
        self.slider.setFixedHeight(36)
        self.slider.startValueChanged.connect(self.set_x_min_view)
        self.slider.endValueChanged.connect(self.set_x_max_view)
        self.layout().addWidget(self.slider)
        self.slider.setHidden(True)

    def set_x_min_view(self, x_min):
        self.x_min = x_min
        self.update_view_range()

    def set_x_max_view(self, x_max):
        self.x_max = x_max
        self.update_view_range()

    def update_view_range(self):
        nx_P, ny_P, nx_L, ny_L, nx_all, ny_all = 0, 1, 2, 3, 4, 5
        # print(np.shape(self.xy_cop))
        # self.plot_COP_global.set_data(self.xy_cop[nx_all], self.xy_cop[ny_all])
        # self.plot_COP_left.set_data(self.xy_cop[nx_L], self.xy_cop[ny_L])
        # self.plot_COP_right.set_data(self.xy_cop[nx_P], self.xy_cop[ny_P])
        self.plot_COP_global.set_data(self.xy_cop[nx_all][self.x_min:self.x_max], self.xy_cop[ny_all][self.x_min:self.x_max])
        self.plot_COP_left.set_data(self.xy_cop[nx_L][self.x_min:self.x_max], self.xy_cop[ny_L][self.x_min:self.x_max])
        self.plot_COP_right.set_data(self.xy_cop[nx_P][self.x_min:self.x_max], self.xy_cop[ny_P][self.x_min:self.x_max])
        self.fig.canvas.draw()

    def get_view_range(self):
        return self.x_min, self.x_max

    def update_canvas(self):
        self.xy_cop = self.data_obj.get_cop(self.nsamp_view)
        nx_P, ny_P, nx_L, ny_L, nx_all, ny_all = 0, 1, 2, 3, 4, 5
        # print(self.y[:, -1])
        # self.fig.canvas.draw()
        # self.fig.axes.clear()
        self.plot_COP_global.set_data(self.xy_cop[nx_all], self.xy_cop[ny_all])
        # self.fig.canvas.draw()
        self.plot_COP_left.set_data(self.xy_cop[nx_L], self.xy_cop[ny_L])
        # self.fig.canvas.draw()
        self.plot_COP_right.set_data(self.xy_cop[nx_P], self.xy_cop[ny_P])
        # self.fig.canvas.show()
        self.fig.canvas.draw()

    def btnstate(self, b):
        if b.text() == "Point":
            self.plot_COP_global.set_visible(point=b.isChecked())
            self.plot_COP_left.set_visible(point=b.isChecked())
            self.plot_COP_right.set_visible(point=b.isChecked())
        elif b.text() == "Show all points":
            self.plot_COP_global.set_show_all_points(b.isChecked())
            self.plot_COP_left.set_show_all_points(b.isChecked())
            self.plot_COP_right.set_show_all_points(b.isChecked())
        elif b.text() == "Histogram":
            self.plot_COP_global.set_visible(hist=b.isChecked())
            self.plot_COP_left.set_visible(hist=b.isChecked())
            self.plot_COP_right.set_visible(hist=b.isChecked())
        elif b.text() == "Curve":
            self.plot_COP_global.set_visible(curve=b.isChecked())
            self.plot_COP_left.set_visible(curve=b.isChecked())
            self.plot_COP_right.set_visible(curve=b.isChecked())
        elif b.text() == "Dark":
            self.plot_COP_global.set_dark_style(b.isChecked())
            self.plot_COP_left.set_dark_style(b.isChecked())
            self.plot_COP_right.set_dark_style(b.isChecked())
        self.fig.canvas.show()
        self.fig.canvas.draw()

    def show_slider(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max
        self.slider.setMin(x_min)
        self.slider.setMax(x_max)
        self.slider.setRange(x_min, x_max)
        # self.slider.update()
        self.slider.setHidden(False)

    def hide_slider(self):
        self.slider.setHidden(True)

    def get_settings(self):
        return [self.b1.isChecked(), self.b2.isChecked(), self.b3.isChecked(), self.b4.isChecked(), self.b5.isChecked()]

    def set_settings(self, settings):
        self.b1.setChecked(settings[0])
        self.b2.setChecked(settings[1])
        self.b3.setChecked(settings[2])
        self.b4.setChecked(settings[3])
        self.b5.setChecked(settings[4])

    def set_autoscale(self, val):
        self.autoscale = val
        self.plot_COP_global.set_autoscale(val)
        self.plot_COP_left.set_autoscale(val)
        self.plot_COP_right.set_autoscale(val)
        if not self.autoscale:
            self.plot_COP_global.set_xy_lim(self.x_lim_g, self.y_lim_g)
            self.plot_COP_left.set_xy_lim(self.x_lim_lr, self.y_lim_lr)
            self.plot_COP_right.set_xy_lim(self.x_lim_lr, self.y_lim_lr)
        try:
            self.update_view_range()
        except:
            self.update_canvas()


    # def show_slider(self):
    #     self.slider = widgets.QRangeSlider()
    #     self.layout().addWidget(self.slider)


    # def startUpdating(self):
    #     self._timer.start()
    #     # print('startUpdating')/

    # def closeEvent(self, event):
    #     del self._timer
    #     print('closeEvent')
