import pytest
import app.services.trends as trends_mod
import app.services.seo as seo_mod


@pytest.fixture(autouse=True)
def clear_service_caches():
    """Reset in-process caches between tests so they don't bleed state."""
    trends_mod._cache.clear()
    seo_mod._cache.clear()
    yield
    trends_mod._cache.clear()
    seo_mod._cache.clear()
