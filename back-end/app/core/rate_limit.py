"""Shared rate limiter instance, kept outside app.main to avoid import cycles."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
