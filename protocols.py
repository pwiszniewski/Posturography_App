import sys
import glob
import serial


def get_ports_list():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def search_connection(self):
    port_list = get_ports_list()
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

class Serial:
    pass

# class receivePort(QThread):
#     message = QtCore.Signal(str)
#     def __init__(self):
#         self.connected = False
#         QThread.__init__(self)
#
#     def run(self):
#         while self.connected:
#             try:
#                 text = self.serial_port.read(1)
#                 if text != '':
#                     self.message.emit(text)
#             except serial.SerialException, e:
#                 connected = False
#
# and the following to connect it up:
#
# serial_thread = receivePort()
# serial_thread.message.connect(write_terminal, QtCore.Qt.QueuedConnection)
# serial_thread.start()
#
# where write_terminal has a signature of:
#
# def write_terminal(text):
#     ui.plain_edit.appendPlainText(text)