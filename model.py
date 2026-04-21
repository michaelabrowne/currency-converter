"""CurrencyModel — data, network, and domain logic. No UI dependencies."""
from __future__ import annotations

import json

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

CURRENCIES: list[tuple[str, str]] = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("JPY", "Japanese Yen"),
    ("CAD", "Canadian Dollar"),
    ("AUD", "Australian Dollar"),
    ("CHF", "Swiss Franc"),
    ("CNY", "Chinese Yuan"),
    ("INR", "Indian Rupee"),
    ("MXN", "Mexican Peso"),
    ("BRL", "Brazilian Real"),
    ("KRW", "South Korean Won"),
    ("VND", "Vietnamese Dong"),
    ("SGD", "Singapore Dollar"),
    ("HKD", "Hong Kong Dollar"),
    ("THB", "Thai Baht"),
]

_API_BASE = "https://open.er-api.com/v6/latest"


class ConversionResult:
    __slots__ = ("code", "name", "rate", "converted", "inverse")

    def __init__(
        self,
        code: str,
        name: str,
        rate: float,
        converted: float,
        inverse: float,
    ) -> None:
        self.code = code
        self.name = name
        self.rate = rate
        self.converted = converted
        self.inverse = inverse


class CurrencyModel(QObject):
    rates_ready = Signal(str, float, list)   # base, amount, list[ConversionResult]
    fetch_error = Signal(str)
    loading_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._net = QNetworkAccessManager(self)
        self._net.finished.connect(self._on_reply)
        self._pending_base = ""
        self._pending_amount = 0.0
        self._pending_targets: list[str] = []
        self._name_map: dict[str, str] = {code: name for code, name in CURRENCIES}

    @property
    def currencies(self) -> list[tuple[str, str]]:
        return CURRENCIES

    def fetch(self, base: str, amount: float, targets: list[str]) -> None:
        self._pending_base = base
        self._pending_amount = amount
        self._pending_targets = list(targets)
        self.loading_changed.emit(True)
        self._net.get(QNetworkRequest(QUrl(f"{_API_BASE}/{base}")))

    def _on_reply(self, reply: QNetworkReply) -> None:
        self.loading_changed.emit(False)

        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.fetch_error.emit(reply.errorString())
            reply.deleteLater()
            return

        try:
            payload = json.loads(bytes(reply.readAll()).decode("utf-8"))
        except Exception as exc:
            self.fetch_error.emit(f"Parse error: {exc}")
            reply.deleteLater()
            return
        finally:
            reply.deleteLater()

        if payload.get("result") != "success":
            self.fetch_error.emit("API returned a failure response.")
            return

        all_rates = payload.get("rates", {})
        results: list[ConversionResult] = [
            ConversionResult(
                code=code,
                name=self._name_map.get(code, code),
                rate=(r := all_rates[code]),
                converted=r * self._pending_amount,
                inverse=1.0 / r if r else 0.0,
            )
            for code in self._pending_targets
            if code in all_rates
        ]
        self.rates_ready.emit(self._pending_base, self._pending_amount, results)
