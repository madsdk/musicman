"""Main window with three-panel splitter layout."""

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from musicman.services.settings import Settings
from musicman.ui.device_panel import DevicePanel
from musicman.ui.device_selector import DeviceSelector
from musicman.ui.library_panel import LibraryPanel
from musicman.ui.queue_panel import QueuePanel
from musicman.ui.settings_dialog import SettingsDialog
from musicman.ui.transfer_progress import TransferProgressDialog
from musicman.services.scanner import scan_directory, read_track
from musicman.workers.download_worker import DownloadWorker
from musicman.workers.scan_worker import ScanWorker
from musicman.workers.transfer_worker import TransferWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._settings = Settings()
        self._thread_pool = QThreadPool()
        self._transfer_worker: TransferWorker | None = None
        self._download_worker: DownloadWorker | None = None
        self._all_tracks: list = []

        self.setWindowTitle("MusicMan")
        self.setMinimumSize(900, 600)

        self._setup_menu()
        self._setup_ui()
        self._setup_statusbar()
        self._restore_state()

        # Load library if root is set
        if self._settings.library_root:
            self._scan_library(self._settings.library_root)
        else:
            self._load_downloads()

        # Load device if path is set
        if self._settings.device_path:
            self._device_selector.set_path(self._settings.device_path)

        # Detect devices
        self._device_selector.refresh_devices()

    def _setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&Settings...", self._open_settings)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close, "Ctrl+Q")

        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("&About", self._show_about)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        # Device selector bar
        self._device_selector = DeviceSelector()
        self._device_selector.device_changed.connect(self._on_device_changed)
        layout.addWidget(self._device_selector, stretch=0)

        # YouTube download bar
        dl_bar = QHBoxLayout()
        self._id_edit = QLineEdit()
        self._id_edit.setPlaceholderText("Video or playlist ID...")
        dl_bar.addWidget(self._id_edit)
        self._video_radio = QRadioButton("Video")
        self._video_radio.setChecked(True)
        dl_bar.addWidget(self._video_radio)
        self._playlist_radio = QRadioButton("Playlist")
        dl_bar.addWidget(self._playlist_radio)
        self._download_btn = QPushButton("Download")
        self._download_btn.clicked.connect(self._on_download)
        self._download_btn.setEnabled(bool(self._settings.download_folder))
        dl_bar.addWidget(self._download_btn)
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.clicked.connect(self._on_stop_download)
        self._stop_btn.setEnabled(False)
        dl_bar.addWidget(self._stop_btn)
        layout.addLayout(dl_bar)

        # Three-panel splitter
        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Library
        self._library_panel = LibraryPanel()
        self._library_panel.add_to_queue.connect(self._on_add_to_queue)
        self._splitter.addWidget(self._library_panel)

        # Center: Queue + Transfer button
        queue_container = QWidget()
        queue_layout = QVBoxLayout(queue_container)
        queue_layout.setContentsMargins(0, 0, 0, 0)
        self._queue_panel = QueuePanel()
        queue_layout.addWidget(self._queue_panel)

        self._transfer_btn = QPushButton("== Transfer ==")
        self._transfer_btn.setMinimumHeight(36)
        self._transfer_btn.clicked.connect(self._on_transfer)
        queue_layout.addWidget(self._transfer_btn)
        self._splitter.addWidget(queue_container)

        # Right: Device
        self._device_panel = DevicePanel()
        self._splitter.addWidget(self._device_panel)

        self._splitter.setSizes([300, 300, 300])
        layout.addWidget(self._splitter, stretch=1)

    def _setup_statusbar(self):
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Ready")

        self._download_progress = QProgressBar()
        self._download_progress.setFixedWidth(150)
        self._download_progress.setRange(0, 100)
        self._download_progress.setVisible(False)
        self._statusbar.addPermanentWidget(self._download_progress)

    def _open_settings(self):
        old_root = self._settings.library_root
        dlg = SettingsDialog(self._settings, self)
        if dlg.exec():
            new_root = self._settings.library_root
            if new_root and new_root != old_root:
                self._scan_library(new_root)
            self._download_btn.setEnabled(bool(self._settings.download_folder))

    def _show_about(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About MusicMan",
            "MusicMan v0.1.0\n\n"
            "Manage music on old-school MP3 players.\n"
            "Handles transcoding and track ordering via filename prefixes.",
        )

    def _scan_library(self, root: str):
        self._statusbar.showMessage(f"Scanning {root}...")
        worker = ScanWorker(Path(root))
        worker.signals.finished.connect(self._on_scan_finished)
        worker.signals.error.connect(self._on_scan_error)
        self._thread_pool.start(worker)

    def _on_scan_finished(self, tracks):
        self._all_tracks = list(tracks)
        self._load_downloads()
        self._library_panel.load_tracks(self._all_tracks)
        self._statusbar.showMessage(f"Loaded {len(self._all_tracks)} tracks.")

    def _load_downloads(self):
        """Scan the download folder and add tracks as <Downloads>."""
        dl_folder = self._settings.download_folder
        if dl_folder and dl_folder != self._settings.library_root:
            dl_path = Path(dl_folder)
            if dl_path.is_dir():
                dl_tracks = scan_directory(dl_path)
                for t in dl_tracks:
                    t.artist = "<Downloads>"
                self._all_tracks.extend(dl_tracks)
        if not self._settings.library_root:
            self._library_panel.load_tracks(self._all_tracks)
            count = len(self._all_tracks)
            if count:
                self._statusbar.showMessage(f"Loaded {count} downloaded track(s).")

    def _on_scan_error(self, msg):
        self._statusbar.showMessage(f"Scan error: {msg}")

    def _on_download(self):
        id_value = self._id_edit.text().strip()
        if not id_value:
            self._statusbar.showMessage("Please enter a video or playlist ID.")
            return

        dl_folder = self._settings.download_folder
        if not dl_folder:
            self._statusbar.showMessage("Set a download folder in Settings first.")
            return

        self._download_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._statusbar.showMessage("Downloading...")
        self._download_progress.setValue(0)
        self._download_progress.setVisible(True)

        is_playlist = self._playlist_radio.isChecked()
        worker = DownloadWorker(id_value, Path(dl_folder), is_playlist=is_playlist)
        worker.signals.finished.connect(self._on_download_finished)
        worker.signals.error.connect(self._on_download_error)
        worker.signals.progress.connect(self._on_download_progress)
        self._download_worker = worker
        self._thread_pool.start(worker)

    def _on_stop_download(self):
        if self._download_worker is not None:
            self._download_worker.cancel()
            self._statusbar.showMessage("Download stopped.")

    def _on_download_progress(self, percent: float, filename: str):
        self._download_progress.setValue(int(percent))
        name = Path(filename).name if filename else ""
        self._statusbar.showMessage(f"Downloading {name}... {percent:.0f}%")

    def _on_download_finished(self, tracks):
        self._download_worker = None
        self._stop_btn.setEnabled(False)
        self._download_progress.setVisible(False)
        self._all_tracks.extend(tracks)
        self._library_panel.load_tracks(self._all_tracks)
        count = len(tracks)
        self._statusbar.showMessage(f"Downloaded {count} track(s).")
        self._id_edit.clear()
        self._download_btn.setEnabled(True)

    def _on_download_error(self, msg):
        self._download_worker = None
        self._stop_btn.setEnabled(False)
        self._download_progress.setVisible(False)
        self._statusbar.showMessage(f"Download error: {msg}")
        self._download_btn.setEnabled(True)

    def _on_device_changed(self, path):
        self._settings.device_path = path
        self._device_panel.set_device_path(path)

    def _on_add_to_queue(self, tracks):
        self._queue_panel.model.add_tracks(tracks)
        self._statusbar.showMessage(f"Added {len(tracks)} track(s) to queue.")

    def _on_transfer(self):
        tracks = self._queue_panel.model.tracks
        if not tracks:
            self._statusbar.showMessage("Queue is empty.")
            return

        device_path = self._device_selector.current_path()
        if not device_path or not Path(device_path).is_dir():
            self._statusbar.showMessage("No valid device path selected.")
            return

        dlg = TransferProgressDialog(self)

        worker = TransferWorker(
            tracks=tracks,
            device_path=Path(device_path),
            mode=self._settings.transcode_mode,
            cbr_bitrate=self._settings.cbr_bitrate,
            vbr_quality=self._settings.vbr_quality,
        )
        worker.signals.progress.connect(dlg.update_progress)
        worker.signals.finished.connect(dlg.transfer_finished)
        worker.signals.finished.connect(lambda _: self._device_panel.refresh())
        worker.signals.error.connect(
            lambda msg: dlg.transfer_finished([f"Fatal: {msg}"])
        )
        dlg.set_cancel_callback(worker.cancel)

        self._transfer_worker = worker
        self._thread_pool.start(worker)
        dlg.exec()
        self._transfer_worker = None

    def _restore_state(self):
        geo = self._settings.load_geometry()
        if geo:
            self.restoreGeometry(geo)
        state = self._settings.load_state()
        if state:
            self.restoreState(state)

    def closeEvent(self, event):
        self._settings.save_geometry(self.saveGeometry())
        self._settings.save_state(self.saveState())
        if self._download_worker is not None:
            self._download_worker.cancel()
        self._thread_pool.clear()
        self._thread_pool.waitForDone(3000)
        super().closeEvent(event)
