from types import SimpleNamespace

import pytest
from t_tech.invest import InstrumentIdType, Quotation

from tinvest_devkit.client import (
    InstrumentResolutionError,
    TInvestReadClient,
)
from tinvest_devkit.config import Settings
from tinvest_devkit.mapper import map_instrument


def sdk_instrument(
    uid="uid-1",
    ticker="SBER",
    class_code="TQBR",
):
    return SimpleNamespace(
        uid=uid,
        ticker=ticker,
        figi="BBG000000001",
        class_code=class_code,
        instrument_type="share",
        name="Sberbank",
        lot=10,
        currency="rub",
        min_price_increment=Quotation(units=0, nano=10_000_000),
        api_trade_available_flag=True,
        position_uid="position-1",
    )


class FakeInstrumentsService:
    def __init__(self, *, instruments=(), instrument=None):
        self.instruments = list(instruments)
        self.instrument = instrument
        self.find_requests = []
        self.get_requests = []

    def find_instrument(self, **kwargs):
        self.find_requests.append(kwargs)
        return SimpleNamespace(instruments=self.instruments)

    def get_instrument_by(self, **kwargs):
        self.get_requests.append(kwargs)
        return SimpleNamespace(instrument=self.instrument)


class FakeSdkClient:
    def __init__(self, token, service):
        self.instruments = service

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def client_for(service):
    return TInvestReadClient(
        Settings(token="synthetic", account_id=None),
        client_factory=lambda token: FakeSdkClient(token, service),
    )


def test_map_instrument_preserves_uid_lot_currency_and_tick():
    instrument = map_instrument(sdk_instrument())

    assert instrument.uid == "uid-1"
    assert instrument.lot == 10
    assert instrument.currency == "rub"
    assert str(instrument.min_price_increment) == "0.01"
    assert instrument.api_trade_available is True


def test_map_instrument_rejects_missing_uid():
    with pytest.raises(ValueError, match="canonical UID"):
        map_instrument(sdk_instrument(uid=""))


def test_get_instrument_requests_uid_and_checks_response_identity():
    service = FakeInstrumentsService(instrument=sdk_instrument())
    instrument = client_for(service).get_instrument("uid-1")

    assert instrument.uid == "uid-1"
    assert service.get_requests == [{
        "id_type": InstrumentIdType.INSTRUMENT_ID_TYPE_UID,
        "id": "uid-1",
    }]


def test_get_instrument_rejects_mismatched_uid():
    service = FakeInstrumentsService(instrument=sdk_instrument(uid="other"))

    with pytest.raises(InstrumentResolutionError, match="different instrument UID"):
        client_for(service).get_instrument("uid-1")


def test_resolve_instrument_requires_unique_ticker_and_class():
    service = FakeInstrumentsService(instruments=[
        sdk_instrument(uid="ru", class_code="TQBR"),
        sdk_instrument(uid="us", class_code="SPBXM"),
    ])

    with pytest.raises(InstrumentResolutionError, match="ambiguous") as error:
        client_for(service).resolve_instrument(" sber ")

    assert {item.class_code for item in error.value.candidates} == {"TQBR", "SPBXM"}
    selected = client_for(service).resolve_instrument("SBER", class_code="TQBR")
    assert selected.uid == "ru"
    assert service.find_requests[0] == {"query": "sber"}


def test_resolve_instrument_rejects_no_exact_ticker_match():
    service = FakeInstrumentsService(instruments=[sdk_instrument(ticker="SBERP")])

    with pytest.raises(InstrumentResolutionError, match="No T-Invest instrument"):
        client_for(service).resolve_instrument("SBER")


def test_resolve_instrument_requires_nonempty_ticker():
    service = FakeInstrumentsService()

    with pytest.raises(ValueError, match="ticker is required"):
        client_for(service).resolve_instrument("  ")
