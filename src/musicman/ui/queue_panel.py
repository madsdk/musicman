"""Transfer queue panel with drag-and-drop reordering."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from musicman.models.transfer_queue import TransferQueueModel


class QueuePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = TransferQueueModel()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setDragEnabled(True)
        self._table.setAcceptDrops(True)
        self._table.setDropIndicatorShown(True)
        self._table.setDragDropMode(QTableView.DragDropMode.InternalMove)
        self._table.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        self._remove_btn = QPushButton("Remove")
        self._remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self._remove_btn)
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self._model.clear)
        btn_layout.addWidget(self._clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    @property
    def model(self) -> TransferQueueModel:
        return self._model

    def _on_remove(self):
        indexes = self._table.selectionModel().selectedRows()
        rows = sorted(set(i.row() for i in indexes), reverse=True)
        for row in rows:
            self._model.remove_track(row)
