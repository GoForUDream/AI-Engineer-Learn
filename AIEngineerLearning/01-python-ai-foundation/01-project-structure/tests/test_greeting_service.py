from app.services.greeting_service import build_greeting


def test_build_greeting():
    assert build_greeting("Khang") == "Hello, Khang! Welcome to our application!"
