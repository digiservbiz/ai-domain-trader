from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.portfolio import PortfolioItem
from app.models.snipe_target import SnipeTarget
from app.models.user import User


def test_user_scoped_records_can_coexist_without_cross_user_unique_constraint():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        first = User(email="one@example.test", hashed_password="x")
        second = User(email="two@example.test", hashed_password="x")
        db.add_all([first, second])
        db.flush()

        db.add_all([
            PortfolioItem(user_id=first.id, domain="shared.example", bought_price=10),
            PortfolioItem(user_id=second.id, domain="shared.example", bought_price=20),
            SnipeTarget(user_id=first.id, domain="watch.example", max_bid=50),
            SnipeTarget(user_id=second.id, domain="watch.example", max_bid=60),
        ])
        db.commit()

        assert db.query(PortfolioItem).filter(PortfolioItem.user_id == first.id).count() == 1
        assert db.query(PortfolioItem).filter(PortfolioItem.user_id == second.id).count() == 1
        assert db.query(SnipeTarget).filter(SnipeTarget.user_id == first.id).count() == 1
        assert db.query(SnipeTarget).filter(SnipeTarget.user_id == second.id).count() == 1
    finally:
        db.close()
        engine.dispose()
