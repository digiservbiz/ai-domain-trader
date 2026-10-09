from datetime import datetime

from app.models.snipe_target import SnipeTarget
from app.tasks import auction


class FakeQuery:
    def __init__(self, target):
        self.target = target
        self.filters = []

    def filter(self, *args):
        self.filters.extend(args)
        return self

    def first(self):
        return self.target


class FakeSession:
    def __init__(self, target):
        self.target = target
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def query(self, model):
        assert model is SnipeTarget
        return FakeQuery(self.target)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


class FakeResponse:
    status_code = 200

    def json(self):
        return {"currentBid": 5}

    def raise_for_status(self):
        return None


class FakeTask:
    def retry(self, **kwargs):
        raise AssertionError("Unexpected retry in successful worker test")


def test_snipe_worker_uses_persisted_target_id_and_bid_cap(monkeypatch):
    target = SnipeTarget(id=22, user_id=2, domain="shared.example", max_bid=40, status="watching")
    session = FakeSession(target)
    monkeypatch.setattr(auction, "_db_session", lambda: session)
    # Test the two independent live gates rather than monkeypatching a read-only property.
    monkeypatch.setattr(auction.settings, "TRADING_MODE", "live")
    monkeypatch.setattr(auction.settings, "LIVE_TRADING_ENABLED", True)
    monkeypatch.setattr(auction.settings, "GODADDY_KEY", "test-key")
    monkeypatch.setattr(auction.settings, "GODADDY_SECRET", "test-secret")

    requests_seen = []

    def fake_get(url, **kwargs):
        requests_seen.append(("get", url))
        return FakeResponse()

    def fake_post(url, **kwargs):
        requests_seen.append(("post", url, kwargs.get("json")))
        return FakeResponse()

    monkeypatch.setattr(auction.requests, "get", fake_get)
    monkeypatch.setattr(auction.requests, "post", fake_post)

    result = auction.snipe.run(FakeTask(), target_id=22)

    assert result == {"skipped": False, "mode": "live", "domain": "shared.example", "bid": 40}
    assert requests_seen[0][1].endswith("/shared.example")
    assert requests_seen[1][2] == {"amount": 40}
    assert target.status == "bid_placed"
    assert isinstance(target.last_checked, datetime)
    assert session.commits == 1
    assert session.closed is True


def test_snipe_worker_does_not_contact_marketplace_in_paper_mode(monkeypatch):
    session_factory_called = False

    def forbidden_session():
        nonlocal session_factory_called
        session_factory_called = True
        raise AssertionError("Paper mode must exit before opening a DB session")

    def forbidden_request(*args, **kwargs):
        raise AssertionError("Paper mode must not contact the marketplace")

    monkeypatch.setattr(auction, "_db_session", forbidden_session)
    monkeypatch.setattr(auction.settings, "TRADING_MODE", "paper")
    monkeypatch.setattr(auction.settings, "LIVE_TRADING_ENABLED", False)
    monkeypatch.setattr(auction.requests, "get", forbidden_request)
    monkeypatch.setattr(auction.requests, "post", forbidden_request)

    result = auction.snipe.run(FakeTask(), target_id=22)

    assert result["mode"] == "paper"
    assert result["skipped"] is True
    assert session_factory_called is False
