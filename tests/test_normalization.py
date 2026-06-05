from sbi_fund_faq.retrieval.normalization import normalize_query


def test_normalize_query_maps_scheme_aliases():
    assert normalize_query("expense ratio for flexicap").scheme_name == "SBI Flexicap Fund"
    assert normalize_query("risk level of elss").scheme_name == "SBI ELSS Tax Saver Fund"
    assert normalize_query("benchmark for largecap").scheme_name == "SBI Large Cap Fund"


def test_normalize_query_maps_field_aliases():
    assert normalize_query("expense ratio for flexicap").field_name == "TER"
    assert normalize_query("risk level of elss").field_name == "riskometer"
    assert normalize_query("SIP minimum for large cap").field_name == "minimum SIP amount"
    assert normalize_query("minimum investment for ELSS").field_name == "minimum application amount"


def test_normalize_query_marks_ambiguous_scheme():
    normalized = normalize_query("What is the expense ratio of SBI fund?")

    assert normalized.scheme_name is None
    assert normalized.is_ambiguous_scheme
