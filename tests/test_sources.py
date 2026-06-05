from sbi_fund_faq.ingestion import (
    approved_source_paths,
    find_unapproved_source_files,
    load_source_registry,
    validate_approved_sources,
)


def test_source_registry_contains_only_approved_sources():
    sources = load_source_registry()

    assert len(sources) == 4
    assert {source.source_name for source in sources} == {
        "SBI Flexicap Fund Factsheet",
        "SBI ELSS Tax Saver Fund Factsheet",
        "SBI Large Cap Fund Factsheet",
        "SBI Total Expense Ratio (TER) Data File",
    }


def test_source_registry_has_scheme_mapping():
    sources = load_source_registry()
    source_by_id = {source.id: source for source in sources}

    assert source_by_id["sbi-flexicap-fund-factsheet-april-2026"].scheme_names == [
        "SBI Flexicap Fund"
    ]
    assert source_by_id["sbi-elss-tax-saver-fund-factsheet-april-2026"].scheme_names == [
        "SBI ELSS Tax Saver Fund"
    ]
    assert source_by_id["sbi-large-cap-fund-factsheet-april-2026"].scheme_names == [
        "SBI Large Cap Fund"
    ]
    assert set(source_by_id["sbi-total-expense-ratio-ter-data-file"].scheme_names) == {
        "SBI Flexicap Fund",
        "SBI ELSS Tax Saver Fund",
        "SBI Large Cap Fund",
    }


def test_approved_source_paths_exist():
    paths = approved_source_paths()

    assert len(paths) == 4
    assert all(path.exists() for path in paths.values())


def test_approved_sources_validate_successfully():
    sources = validate_approved_sources()

    assert len(sources) == 4


def test_no_unapproved_source_files_are_visible_to_ingestion():
    assert find_unapproved_source_files() == []
