import matplotlib.pyplot as plt
import numpy as np

# plt.style.use('seaborn')  # ggplot
plt.switch_backend('Qt5Agg')


class LivePlot:
    def __init__(self, ax, x, y, n, y_lim, colors, labels, autoscale=False):
        # plt.style.use('seaborn')  # ggplot
        # plt.switch_backend('Qt5Agg')
        self.lines = []
        self.ax = ax
        self.n = n
        self.y_lim = y_lim
        self.autoscale = autoscale
        for i in range(n):
            line, = ax.plot(x, y[i], color=colors[i], label=labels[i])
            self.lines.append(line)
        self.lines[0].axes.relim()
        self.lines[0].axes.autoscale_view(True, True, True)
        ax.set_title('Weight distribution')
        ax.set_xlabel('Time [min:sec]', ha='center', labelpad=10)
        ax.set_ylabel('Weight [kg]', va='center', rotation='vertical', labelpad=10)
        ax.grid(True, which='major', linestyle='--', linewidth=0.5)
        ax.legend(loc="upper left")
        if self.autoscale:
            ax.autoscale(enable=True, axis='y')
        else:
            ax.set_ylim(y_lim)

    def set_data(self, x, y):
        for i in range(self.n):
            self.lines[i].set_data(x, y[i])

    def update(self):
        # self.ax.clear()
        self.ax.relim()
        # self.ax.autoscale_view(True, True, True)
        if self.autoscale:
            self.ax.autoscale()
        else:
            self.ax.autoscale(axis='x')
        self.ax.figure.canvas.show()

    def set_y_lim(self, y_lim):
        print(y_lim)
        self.y_lim = y_lim
        self.ax.set_ylim(y_lim)

    def set_autoscale(self, val):
        self.autoscale = val


class PointPlot:
    def __init__(self, ax, x, y, x_lim, y_lim, title=None, x_label=None, y_label=None, y_offset=0):
        self.ax = ax
        self._is_visible = True
        self.y_offset = y_offset
        self.point, = ax.plot(x, y, 'o', color='#f25d46', markersize=10)
        self.point.axes.set_ylim(y_lim)
        self.point.axes.set_xlim(x_lim)
        ax.set_title(title)
        ax.set_xlabel(x_label, ha='center', fontsize=12)
        ax.set_ylabel(y_label, va='center', rotation='vertical', fontsize=12)

    def set_data(self, x, y):
        # print('point plot ', x, y+self.y_offset)
        self.point.set_data(x, y + self.y_offset)

    def update(self):
        self.ax.figure.canvas.draw()

    def set_visible(self, val):
        self._is_visible = val
        if val:
            self.point.set_alpha(1)
        else:
            self.point.set_alpha(0)

    def is_visible(self):
        return self._is_visible

    def set_markersize(self, val):
        self.point.set_markersize(val)

class CurvePlot:
    def __init__(self, ax, x, y, x_lim, y_lim, title=None, x_label=None, y_label=None, y_offset=0):
        self.ax = ax
        self._is_visible = True
        self.y_offset = y_offset
        self.curve, = ax.plot(x, y, color='orange', linewidth=1)
        self.curve.axes.set_ylim(y_lim)
        self.curve.axes.set_xlim(x_lim)
        ax.set_title(title)
        ax.set_xlabel(x_label, ha='center', fontsize=12)
        ax.set_ylabel(y_label, va='center', rotation='vertical', fontsize=12)

    def set_data(self, x, y):
        self.curve.set_data(x, y + self.y_offset)

    def update(self):
        # self.ax.relim()
        # self.ax.autoscale_view(True, True, True)
        self.ax.figure.canvas.draw()

    def set_visible(self, val):
        self._is_visible = val
        if val:
            self.curve.set_alpha(1)
        else:
            self.curve.set_alpha(0)

    def is_visible(self):
        return self._is_visible

class HistogramPlot:
    def __init__(self, ax, x, y, x_lim, y_lim, hist_size, y_offset=0, show_bar=False, bar_ax=None):
        self.ax = ax
        self._is_visible = True
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.y_offset = y_offset
        self.hist_size = hist_size
        hist, xedges, yedges = np.histogram2d(x, y, self.hist_size, (x_lim, y_lim))
        extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
        # extent = (yedges[0], yedges[-1], xedges[-1], xedges[0]) # extent=[horizontal_min,horizontal_max,vertical_min,vertical_max]
        self.hist = ax.imshow(hist.T, extent=extent, aspect='auto', cmap=None, interpolation='nearest') #gaussian nearest
        if show_bar:
            self.bar = ax.figure.colorbar(self.hist, cax=bar_ax, orientation='horizontal')
        else:
            self.bar = None

    def set_data(self, x, y, x_lim=None, y_lim=None):
        if x_lim:
            self.x_lim = x_lim
            self.y_lim = y_lim
            hist, xedges, yedges = np.histogram2d(x, y, self.hist_size, (self.x_lim, self.y_lim))
            ext = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
            self.hist.set_extent(ext)
        else:
            hist, _, _ = np.histogram2d(x, y, self.hist_size, (self.x_lim, self.y_lim))
        # hist, _, _ = np.histogram2d(x, y + self.y_offset, self.hist_size, (self.x_lim, self.y_lim))
        self.hist.set_data(hist.T)
        self.hist.set_clim(vmax=np.max(hist))

    def update(self):
        # self.ax.relim()
        # self.ax.autoscale_view(True, True, True)
        self.ax.figure.canvas.draw()

    def set_visible(self, val):
        self._is_visible = val
        if val:
            self.hist.set_alpha(1)
            if self.bar is not None:
                self.bar.set_alpha(1)
                self.bar.draw_all()
        else:
            self.hist.set_alpha(0)
            if self.bar is not None:
                self.bar.set_alpha(0)
                self.bar.draw_all()

    def is_visible(self):
        return self._is_visible


class CombinedPointCurveHistogramPlot:
    def __init__(self, ax, x, y, x_lim, y_lim, hist_size, y_offset=0, show_bar=False, bar_ax=None, title=None,
                 x_label=None, y_label=None, autoscale=False):
        self.ax = ax
        self.x, self.y = None, None
        self.x_lim = x_lim
        self.y_lim = y_lim
        self.curve = CurvePlot(ax, x[-1], y[-1], x_lim, y_lim, None, x_label, y_label, y_offset)
        self.hist = HistogramPlot(ax, x, y, x_lim, y_lim, hist_size, y_offset, show_bar, bar_ax)
        self.point = PointPlot(ax, x[-1], y[-1], x_lim, y_lim, None, x_label, y_label, y_offset)
        ax.set_title(title)
        ax.grid(True, which='major', linestyle='--', linewidth=0.5)
        self._hist_vis, self._curve_vis, self._point_vis = True, True, True
        self.show_all_points = False
        self.autoscale = autoscale

    def set_data(self, x, y):
        self.x, self.y = x, y
        if self.autoscale:
            xmin, xmax, ymin, ymax = np.min(x), np.max(x), np.min(y), np.max(y)
            # self.x_lim = np.copysign(np.abs(xmin)//2*2, xmin) - 1, np.copysign(np.abs(xmin)//2*2, xmin) + 1
            # self.y_lim = np.copysign(np.abs(ymin)//2*2, ymin) - 1, np.copysign(np.abs(ymax)//2*2, ymax) + 1
            # self.x_lim = np.min(x)//2*2, np.max(x)//2*2 + 2
            # self.y_lim = np.min(y)//2*2, np.max(y)//2*2 + 2
            self.x_lim = (xmin - 0.5, xmax + 0.5)
            self.y_lim = (ymin - 0.5, ymax + 0.5)
        if self._curve_vis:
            self.curve.set_data(x, y)
        if self._hist_vis:
            # self.hist.set_data(x, y)
            self.hist.set_data(x, y, self.x_lim, self.y_lim)
        if self._point_vis:
            if self.show_all_points:
                self.point.set_data(x, y)
            else:
                self.point.set_data(x[-1], y[-1])
        self.ax.set_xlim(self.x_lim)
        self.ax.set_ylim(self.y_lim)

    def update(self):
        self.ax.figure.canvas.draw()

    def set_visible(self, point=None, curve=None, hist=None):
        # print('clear')
        if point is not None:
            self._point_vis = point
            self.point.set_visible(self._point_vis)
            # self.point.update()
        if curve is not None:
            self._curve_vis = curve
            self.curve.set_visible(self._curve_vis)
            # self.curve.update()
        if hist is not None:
            self._hist_vis = hist
            self.hist.set_visible(self._hist_vis)
        # print(self._point_vis, self._curve_vis, self._hist_vis)

    def set_xy_lim(self, x_lim, y_lim):
        self.x_lim = x_lim
        self.y_lim = y_lim

    def set_autoscale(self, val):
        self.autoscale = val

    def set_show_all_points(self, val):
        self.show_all_points = val
        if self._point_vis:
            if self.show_all_points:
                self.point.set_markersize(1)
                self.point.set_data(self.x, self.y)
            else:
                self.point.set_markersize(10)
                self.point.set_data(self.x[-1], self.y[-1])

    def set_dark_style(self, val):
        import matplotlib.colors as colors
        def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
            new_cmap = colors.LinearSegmentedColormap.from_list(
                'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
                cmap(np.linspace(minval, maxval, n)))
            return new_cmap
        if val:
            self.point.point.set_color('#f25d46')
            self.curve.curve.set_color('black')
            cmap = plt.get_cmap('bone_r')
            new_cmap = truncate_colormap(cmap, 0, 0.7)
            self.hist.hist.set_cmap(new_cmap)
            # self.hist.hist.set_cmap('bone_r')
        else:
            self.point.point.set_color('#f25d46')
            self.curve.curve.set_color('orange')
            self.hist.hist.set_cmap('viridis')
