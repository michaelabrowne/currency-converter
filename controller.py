"""AppController — wires model signals to view and view signals to model."""
from __future__ import annotations

from model import CurrencyModel
from view import MainWindow


class AppController:
    def __init__(self, model: CurrencyModel, view: MainWindow) -> None:
        self._model = model
        self._view = view
        self._wire()

    def _wire(self) -> None:
        self._view.convert_clicked.connect(self._on_convert)
        self._model.rates_ready.connect(self._view.show_results)
        self._model.fetch_error.connect(self._view.show_error)
        self._model.loading_changed.connect(self._view.set_loading)

    def _on_convert(self, amount: float, base: str, targets: list[str]) -> None:
        if not targets:
            self._view.show_error("Select at least one target currency.")
            return
        filtered = [t for t in targets if t != base]
        if not filtered:
            self._view.show_error("Target currencies must differ from the source.")
            return
        self._model.fetch(base, amount, filtered)
