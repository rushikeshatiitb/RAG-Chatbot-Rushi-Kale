from sbi_fund_faq.chatbot.guardrails import REFUSAL_RESPONSE, classify_question


def test_classifier_refuses_investment_advice_questions():
    examples = [
        "Should I invest in SBI Flexicap Fund?",
        "Which fund is better?",
        "Should I buy or sell SBI Large Cap Fund?",
        "Is SBI ELSS Tax Saver Fund good for me?",
    ]

    for question in examples:
        classification = classify_question(question)
        assert classification.is_advice
        assert classification.refusal_response == REFUSAL_RESPONSE


def test_classifier_allows_factual_questions():
    examples = [
        "What is the expense ratio of SBI Flexicap Fund?",
        "What is the benchmark index for SBI Large Cap Fund?",
        "What is the minimum investment amount?",
        "What is the investment objective of SBI ELSS Tax Saver Fund?",
    ]

    for question in examples:
        assert not classify_question(question).is_advice
