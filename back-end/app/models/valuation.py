import joblib, tldextract, os
from app.services.trends import gscore
from app.services.seo import moz_metrics
model_path = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'xgb_valuation.pkl')
model = joblib.load(model_path) if os.path.exists(model_path) else None
def features(domain: str) -> list:
    ext = tldextract.extract(domain)
    return [len(ext.domain), len(ext.suffix), sum(c in 'aeiou' for c in ext.domain),
            gscore(ext.domain), moz_metrics(domain).get("domain_authority", 0)]
def value(domain: str) -> float:
    return float(model.predict([features(domain)])[0]) if model else 50.0
