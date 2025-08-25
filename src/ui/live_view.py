import sys
import os
import threading
import queue
import datetime as dt
from typing import Optional, Dict, Any, List

from src.core.lynx_thermal_cycle import LynxThermalCycleManager
from src.utils.logging_utils import log_queue


def run_gui():  # pragma: no cover - convenience entrypoint
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets  # type: ignore
        import pyqtgraph as pg  # type: ignore
    except (ImportError, ModuleNotFoundError):
        print("PyQt5/pyqtgraph not installed. Install with: pip install PyQt5 pyqtgraph")
        return

    class QTextEditLogger(QtGui.QTextEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)
            self.setMinimumHeight(120)

        @QtCore.pyqtSlot(str)
        def append_line(self, line: str):
            self.append(line)
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    class LiveTelemetryModel(QtCore.QObject):
        telemetry = QtCore.pyqtSignal(dict)

    class LiveWindow(QtWidgets.QMainWindow):
        def __init__(self, manager: LynxThermalCycleManager, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Lynx Thermal Cycle - Live")
            self.resize(1000, 700)
            self.manager = manager

            central = QtWidgets.QWidget(self)
            self.setCentralWidget(central)
            layout = QtWidgets.QVBoxLayout(central)

            # Plot: temperatures and PSU
            self.plot = pg.PlotWidget(background='k')
            self.plot.addLegend()
            self.plot.setLabel('bottom', 'Time', 's')
            self.plot.setLabel('left', 'Temperature (C) / PSU')
            layout.addWidget(self.plot)

            self.curve_actual = self.plot.plot(pen=pg.mkPen('y', width=2), name='Actual Temp')
            self.curve_target = self.plot.plot(pen=pg.mkPen('c', style=QtCore.Qt.DashLine), name='Target')
            self.curve_setpoint = self.plot.plot(pen=pg.mkPen('m', style=QtCore.Qt.DotLine), name='Setpoint')
            self.curve_v = self.plot.plot(pen=pg.mkPen('g', width=1), name='PSU V')
            self.curve_c = self.plot.plot(pen=pg.mkPen('r', width=1), name='PSU A')

            # Log viewer
            self.log_view = QTextEditLogger(self)
            layout.addWidget(self.log_view)

            # Controls
            ctrl_layout = QtWidgets.QHBoxLayout()
            layout.addLayout(ctrl_layout)
            self.btn_start = QtWidgets.QPushButton("Start Profile…")
            self.btn_start.clicked.connect(self.choose_and_start)
            ctrl_layout.addWidget(self.btn_start)
            self.lbl_status = QtWidgets.QLabel("Idle")
            ctrl_layout.addWidget(self.lbl_status, 1)

            # Data storage for plots
            self.t0: Optional[float] = None
            self.t: List[float] = []
            self.actual: List[Optional[float]] = []
            self.target: List[Optional[float]] = []
            self.setpoint: List[Optional[float]] = []
            self.v: List[Optional[float]] = []
            self.c: List[Optional[float]] = []

            # Telemetry signal model
            self.model = LiveTelemetryModel()
            self.model.telemetry.connect(self.on_telemetry)

            # Start a timer to pump log messages from logging_utils.log_queue
            self.log_timer = QtCore.QTimer(self)
            self.log_timer.timeout.connect(self.drain_log_queue)
            self.log_timer.start(200)

            # Register callback to manager
            self.manager.set_telemetry_callback(self._telemetry_callback)

        def choose_and_start(self):
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Thermal Profile JSON", os.getcwd(), "JSON (*.json)")
            if not path:
                return
            self.lbl_status.setText(f"Running: {os.path.basename(path)}")
            thread = threading.Thread(target=self.manager.run_thermal_cycle, args=(path,), daemon=True)
            thread.start()

        def _telemetry_callback(self, payload: Dict[str, Any]):
            # shift to Qt thread via signal
            self.model.telemetry.emit(payload)

        @QtCore.pyqtSlot(dict)
        def on_telemetry(self, payload: Dict[str, Any]):
            # Update time vector
            ts = payload.get('timestamp', dt.datetime.now())
            if self.t0 is None:
                self.t0 = ts.timestamp()
            t = ts.timestamp() - self.t0
            self.t.append(t)

            # Extract values
            def to_num(val):
                return float(val) if isinstance(val, (int, float)) else None

            self.actual.append(to_num(payload.get('actual_temp_c')))
            self.target.append(to_num(payload.get('target_c')))
            self.setpoint.append(to_num(payload.get('setpoint_c')))
            self.v.append(to_num(payload.get('psu_voltage')))
            self.c.append(to_num(payload.get('psu_current')))

            # Update curves with non-None filtering
            def clean(data):
                return [x if isinstance(x, (int, float)) else None for x in data]

            self.curve_actual.setData(self.t, clean(self.actual))
            self.curve_target.setData(self.t, clean(self.target))
            self.curve_setpoint.setData(self.t, clean(self.setpoint))
            self.curve_v.setData(self.t, clean(self.v))
            self.curve_c.setData(self.t, clean(self.c))

            # Status text
            phase = payload.get('phase', '')
            step = payload.get('step_name', '')
            self.lbl_status.setText(f"{phase} — {step}")

        def drain_log_queue(self):
            try:
                while True:
                    msg = log_queue.get_nowait()
                    self.log_view.append_line(msg)
            except queue.Empty:
                pass

    app = QtWidgets.QApplication(sys.argv)
    manager = LynxThermalCycleManager()
    win = LiveWindow(manager)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":  # pragma: no cover
    run_gui()
