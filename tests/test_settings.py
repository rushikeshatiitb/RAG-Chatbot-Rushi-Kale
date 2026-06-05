from sbi_fund_faq.config import get_settings


def test_settings_load_defaults():
    settings = get_settings()

    assert settings.app_name == "SBI Mutual Fund FAQ Assistant"
    assert settings.source_docs_dir.as_posix() == "data/source_docs"
    assert settings.source_registry_path.as_posix() == "data/source_registry.json"
    assert settings.vector_store_dir.as_posix() == "data/vector_store"
