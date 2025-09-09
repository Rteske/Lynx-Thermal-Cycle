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
        from PyQt5 import QtCore, QtWidgets  # type: ignore
        import pyqtgraph as pg  # type: ignore
    except (ImportError, ModuleNotFoundError):
        print("PyQt5/pyqtgraph not installed. Install with: pip install PyQt5 pyqtgraph")
        return

    class QTextEditLogger(QtWidgets.QTextEdit):
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
            self.curve_tc1 = self.plot.plot(pen=pg.mkPen(color=(255, 165, 0), width=1), name='TC1 C')
            self.curve_tc2 = self.plot.plot(pen=pg.mkPen(color=(173, 216, 230), width=1), name='TC2 C')

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
            self.tc1: List[Optional[float]] = []
            self.tc2: List[Optional[float]] = []

            # Telemetry signal model
            self.model = LiveTelemetryModel()
            self.model.telemetry.connect(self.on_telemetry)

            # Start a timer to pump log messages from logging_utils.log_queue
            self.log_timer = QtCore.QTimer(self)
            self.log_timer.timeout.connect(self.drain_log_queue)
            self.log_timer.start(200)

            # Register callback to manager
            self.manager.set_telemetry_callback(self._telemetry_callback)
            # Note: test_manager telemetry is already forwarded by the thermal manager's callback.
            # Setting both would double-emit into the GUI; keep only the manager callback.

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

        def _coerce_timestamp(self, ts_val: Any) -> dt.datetime:
            """Best-effort conversion of various timestamp representations to datetime."""
            try:
                if isinstance(ts_val, dt.datetime):
                    return ts_val
                if isinstance(ts_val, (int, float)):
                    # treat as POSIX seconds
                    return dt.datetime.fromtimestamp(float(ts_val))
                if isinstance(ts_val, str):
                    # try ISO8601 first
                    try:
                        return dt.datetime.fromisoformat(ts_val)
                    except Exception:
                        # common fallback: parse 'YYYY-MM-DD HH:MM:SS' (no timezone)
                        try:
                            return dt.datetime.strptime(ts_val, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            # give up, return now
                            return dt.datetime.now()
            except Exception:
                pass
            return dt.datetime.now()

        def _first(self, payload: Dict[str, Any], *keys: str) -> Any:
            for k in keys:
                if k in payload and payload[k] is not None:
                    return payload[k]
            return None

        @QtCore.pyqtSlot(dict)
        def on_telemetry(self, payload: Dict[str, Any]):
            # Consume payload as-is; do not query instruments from GUI thread.

            # Update time vector
            ts_raw = self._first(payload, 'timestamp', 'ts', 'time')
            ts = self._coerce_timestamp(ts_raw)
            if self.t0 is None:
                self.t0 = ts.timestamp()
            t = ts.timestamp() - self.t0
            self.t.append(t)

            # Extract values
            def to_num(val):
                return float(val) if isinstance(val, (int, float)) else None

            # Accept a few common aliases for resilience across emitters
            self.actual.append(to_num(self._first(payload, 'actual_temp_c', 'actual_c', 'controller_actual_c')))
            self.target.append(to_num(self._first(payload, 'target_c', 'target_temp_c', 'target')))
            self.setpoint.append(to_num(self._first(payload, 'setpoint_c', 'temp_setpoint_c', 'controller_setpoint_c')))
            self.v.append(to_num(self._first(payload, 'psu_voltage', 'psu_v', 'voltage')))
            self.c.append(to_num(self._first(payload, 'psu_current', 'psu_i', 'current')))
            self.tc1.append(to_num(self._first(payload, 'tc1_temp', 'tc1_c', 'tc_1_c')))
            self.tc2.append(to_num(self._first(payload, 'tc2_temp', 'tc2_c', 'tc_2_c')))

            # Update curves with non-None filtering
            def clean(data):
                return [x if isinstance(x, (int, float)) else 0 for x in data]

            self.curve_actual.setData(self.t, clean(self.actual))
            self.curve_target.setData(self.t, clean(self.target))
            self.curve_setpoint.setData(self.t, clean(self.setpoint))
            self.curve_v.setData(self.t, clean(self.v))
            self.curve_c.setData(self.t, clean(self.c))
            self.curve_tc1.setData(self.t, clean(self.tc1))
            self.curve_tc2.setData(self.t, clean(self.tc2))

            # Status text
            phase = self._first(payload, 'phase', 'test_phase') or ''
            step = self._first(payload, 'step_name', 'step') or ''
            self.lbl_status.setText(f"{phase} — {step}")

        def drain_log_queue(self):
            try:
                while True:
                    msg = log_queue.get_nowait()
                    self.log_view.append_line(msg)
            except queue.Empty:
                pass

    app = QtWidgets.QApplication(sys.argv)
    # Use simulation mode by default for development
    manager = LynxThermalCycleManager(simulation_mode=False)
    win = LiveWindow(manager)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":  # pragma: no cover
    run_gui()
