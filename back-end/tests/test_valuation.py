from unittest.mock import patch
import app.models.valuation as v


def test_features_length_vowels_tld():
    with patch("app.models.valuation.gscore", return_value=75), \
         patch("app.models.valuation.moz_metrics", return_value={"domain_authority": 40}):
        f = v.features("example.com")
    # "example" -> len 7, vowels e,a,e = 3; "com" -> len 3
    assert f[0] == 7   # domain length
    assert f[1] == 3   # tld length
    assert f[2] == 3   # vowel count
    assert f[3] == 75  # trends score
    assert f[4] == 40  # domain authority


def test_features_no_vowels():
    with patch("app.models.valuation.gscore", return_value=0), \
         patch("app.models.valuation.moz_metrics", return_value={"domain_authority": 0}):
        f = v.features("xyz.io")
    assert f[2] == 0


def test_value_fallback_when_no_model():
    original = v.model
    v.model = None
    try:
        assert v.value("test.com") == 50.0
    finally:
        v.model = original


def test_value_uses_model_predict():
    with patch("app.models.valuation.gscore", return_value=50), \
         patch("app.models.valuation.moz_metrics", return_value={"domain_authority": 20}):
        if v.model is not None:
            result = v.value("example.com")
            assert isinstance(result, float)
