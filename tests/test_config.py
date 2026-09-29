from app.core.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.chunk_size > settings.chunk_overlap
    assert settings.top_k >= 1
    assert settings.embedding_model
