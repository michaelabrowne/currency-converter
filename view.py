"""MainWindow — all UI widgets and layout. Zero business logic."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from model import CURRENCIES, DEFAULT_CURRENCY, ConversionResult

# ── stylesheet ────────────────────────────────────────────────────────────────

_QSS = """
QMainWindow, QWidget { background: #0f172a; color: #e2e8f0; }

/* left panel */
QFrame#panel {
    background: #1e293b;
    border-right: 1px solid #2d3f55;
}

/* inputs */
QDoubleSpinBox, QComboBox {
    background: #0f172a;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 14px;
    min-height: 22px;
}
QDoubleSpinBox:focus, QComboBox:focus { border-color: #6366f1; }
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: #1e293b;
    border: none;
    width: 18px;
}
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: #334155;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    selection-background-color: #4f46e5;
    selection-color: #fff;
    outline: 0;
}

/* currency checklist */
QListWidget {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    outline: 0;
    padding: 3px;
}
QListWidget::item {
    border-radius: 4px;
    padding: 5px 6px;
    color: #cbd5e1;
    font-size: 13px;
}
QListWidget::item:hover { background: #1e293b; }
QListWidget::item:selected { background: transparent; color: #cbd5e1; }
QListWidget::indicator {
    width: 15px; height: 15px;
    border-radius: 3px;
    border: 1.5px solid #475569;
    background: #0f172a;
}
QListWidget::indicator:checked {
    background: #6366f1;
    border-color: #6366f1;
}
QListWidget::indicator:checked:hover { background: #4f46e5; }
QListWidget::indicator:hover { border-color: #818cf8; }

/* convert button */
QPushButton#convert {
    background: #6366f1;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-size: 15px;
    font-weight: 600;
}
QPushButton#convert:hover { background: #4f46e5; }
QPushButton#convert:pressed { background: #4338ca; }
QPushButton#convert:disabled { background: #334155; color: #64748b; }

/* small utility buttons */
QPushButton#small {
    background: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
    border-radius: 5px;
    padding: 4px 9px;
    font-size: 12px;
}
QPushButton#small:hover { background: #334155; color: #e2e8f0; }

/* error banner */
QLabel#error {
    background: #450a0a;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}

/* result cards */
QFrame#card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}
QFrame#card:hover { border-color: #4f46e5; }

/* scroll bars */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #0f172a; width: 7px; border-radius: 3px; margin: 0;
}
QScrollBar::handle:vertical {
    background: #334155; border-radius: 3px; min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #475569; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* splitter handle */
QSplitter::handle { background: #2d3f55; }
"""


# ── helpers ───────────────────────────────────────────────────────────────────

def _fmt(value: float) -> str:
    if value >= 1_000:
        return f"{value:,.2f}"
    if value >= 1:
        return f"{value:.4f}"
    return f"{value:.6f}"


def _lbl(text: str, obj_name: str = "", px: int = 0, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    if obj_name:
        lbl.setObjectName(obj_name)
    if px or bold:
        f = lbl.font()
        if px:
            f.setPixelSize(px)
        if bold:
            f.setWeight(QFont.Weight.Bold)
        lbl.setFont(f)
    return lbl


# ── result card ───────────────────────────────────────────────────────────────

class ResultCard(QFrame):
    def __init__(self, base: str, amount: float, result: ConversionResult) -> None:
        super().__init__()
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 11, 16, 11)
        layout.setSpacing(4)

        main = QLabel(
            f'<span style="color:#94a3b8">{_fmt(amount)} {base}</span>'
            f'<span style="color:#475569"> &rarr; </span>'
            f'<span style="color:#a5b4fc;font-weight:600">{_fmt(result.converted)} {result.code}</span>'
            f'<span style="color:#64748b;font-size:12px"> {result.name}</span>'
        )
        main.setTextFormat(Qt.TextFormat.RichText)
        f = main.font()
        f.setPixelSize(16)
        main.setFont(f)
        layout.addWidget(main)

        rates = QLabel(
            f'<span style="color:#475569">Rate: </span>'
            f'<span style="color:#7c8fac">1 {base} = {_fmt(result.rate)} {result.code}</span>'
            f'<span style="color:#2d3f55"> · </span>'
            f'<span style="color:#475569">Inverse: </span>'
            f'<span style="color:#7c8fac">1 {result.code} = {_fmt(result.inverse)} {base}</span>'
        )
        rates.setTextFormat(Qt.TextFormat.RichText)
        f2 = rates.font()
        f2.setPixelSize(12)
        rates.setFont(f2)
        layout.addWidget(rates)


# ── main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    convert_clicked = Signal(float, str, list)   # amount, base, [target codes]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Currency Converter")
        self.setMinimumSize(820, 520)
        self.resize(1020, 680)
        self.setStyleSheet(_QSS)
        self._build_ui()

    # ── public interface (called by controller) ───────────────────────────────

    def show_results(self, base: str, amount: float, results: list[ConversionResult]) -> None:
        self._clear_cards()
        for r in results:
            self._results_layout.addWidget(ResultCard(base, amount, r))
        self._right_stack.setCurrentIndex(1)

    def show_error(self, msg: str) -> None:
        self._error_lbl.setText(msg)
        self._error_lbl.show()

    def clear_error(self) -> None:
        self._error_lbl.hide()

    def set_loading(self, loading: bool) -> None:
        self._convert_btn.setEnabled(not loading)
        self._convert_btn.setText("Fetching rates…" if loading else "Convert")

    def get_amount(self) -> float:
        return self._amount_spin.value()

    def get_base(self) -> str:
        return self._base_combo.currentData()

    def get_selected_targets(self) -> list[str]:
        return [
            self._list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._list.count())
            if self._list.item(i).checkState() == Qt.CheckState.Checked
        ]

    # ── builders ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        root.addWidget(splitter)

        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([310, 710])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _build_left_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumWidth(270)
        panel.setMaximumWidth(380)

        lo = QVBoxLayout(panel)
        lo.setContentsMargins(20, 24, 20, 20)
        lo.setSpacing(14)

        # Title
        title = _lbl("Currency Converter", px=20, bold=True)
        title.setStyleSheet("color:#f8fafc;")
        lo.addWidget(title)

        # Amount + From row
        row = QHBoxLayout()
        row.setSpacing(10)

        amt_col = QVBoxLayout()
        amt_col.setSpacing(4)
        amt_col.addWidget(_lbl("Amount", "fieldlabel"))
        self._amount_spin = QDoubleSpinBox()
        self._amount_spin.setRange(0.0, 1_000_000_000.0)
        self._amount_spin.setValue(100.0)
        self._amount_spin.setDecimals(2)
        self._amount_spin.setGroupSeparatorShown(True)
        amt_col.addWidget(self._amount_spin)
        row.addLayout(amt_col, 3)

        from_col = QVBoxLayout()
        from_col.setSpacing(4)
        from_col.addWidget(_lbl("From", "fieldlabel"))
        self._base_combo = QComboBox()
        for code, name in CURRENCIES:
            self._base_combo.addItem(f"{code}  {name}", code)
        default_idx = next(
            (i for i in range(self._base_combo.count())
             if self._base_combo.itemData(i) == DEFAULT_CURRENCY), 0
        )
        self._base_combo.setCurrentIndex(default_idx)
        self._base_combo.currentIndexChanged.connect(self._on_base_changed)
        from_col.addWidget(self._base_combo)
        row.addLayout(from_col, 4)

        lo.addLayout(row)

        # "Convert to" header + All/None buttons
        hdr = QHBoxLayout()
        hdr.addWidget(_lbl("Convert to", "fieldlabel"))
        hdr.addStretch()
        for label, slot in (("All", self._select_all), ("None", self._select_none)):
            btn = QPushButton(label)
            btn.setObjectName("small")
            btn.setFixedWidth(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            hdr.addWidget(btn)
        lo.addLayout(hdr)

        # Currency checklist
        self._list = QListWidget()
        defaults = {"USD", "GBP", "JPY"}
        for code, name in CURRENCIES:
            item = QListWidgetItem(f"  {code}   {name}")
            item.setData(Qt.ItemDataRole.UserRole, code)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if code in defaults else Qt.CheckState.Unchecked
            )
            self._list.addItem(item)
        lo.addWidget(self._list, stretch=1)

        # Hide the default "From" currency from the checklist on startup
        self._on_base_changed()

        # Error banner (hidden by default)
        self._error_lbl = QLabel()
        self._error_lbl.setObjectName("error")
        self._error_lbl.setWordWrap(True)
        self._error_lbl.hide()
        lo.addWidget(self._error_lbl)

        # Convert button
        self._convert_btn = QPushButton("Convert")
        self._convert_btn.setObjectName("convert")
        self._convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._convert_btn.clicked.connect(self._on_convert_clicked)
        lo.addWidget(self._convert_btn)

        return panel

    def _build_right_panel(self) -> QStackedWidget:
        self._right_stack = QStackedWidget()
        self._right_stack.setStyleSheet("background: #0f172a;")

        # Page 0 — placeholder
        ph_page = QWidget()
        ph_page.setStyleSheet("background: #0f172a;")
        ph_lo = QVBoxLayout(ph_page)
        hint = _lbl("Select currencies and press  Convert", px=15)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #2d3f55;")
        ph_lo.addWidget(hint)
        self._right_stack.addWidget(ph_page)   # index 0

        # Page 1 — scrollable results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._results_widget = QWidget()
        self._results_widget.setStyleSheet("background: #0f172a;")
        self._results_layout = QVBoxLayout(self._results_widget)
        self._results_layout.setContentsMargins(20, 20, 20, 20)
        self._results_layout.setSpacing(10)
        self._results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self._results_widget)
        self._right_stack.addWidget(scroll)    # index 1

        return self._right_stack

    # ── internal helpers ──────────────────────────────────────────────────────

    def _clear_cards(self) -> None:
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_base_changed(self) -> None:
        base = self.get_base()
        for i in range(self._list.count()):
            item = self._list.item(i)
            item.setHidden(item.data(Qt.ItemDataRole.UserRole) == base)

    def _select_all(self) -> None:
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(Qt.CheckState.Checked)

    def _select_none(self) -> None:
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _on_convert_clicked(self) -> None:
        self.clear_error()
        self.convert_clicked.emit(
            self.get_amount(),
            self.get_base(),
            self.get_selected_targets(),
        )
