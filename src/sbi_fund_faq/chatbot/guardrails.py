import re
from dataclasses import dataclass


REFUSAL_RESPONSE = (
    "I cannot provide investment advice or recommendations. "
    "I can only provide factual information from official SBI Mutual Fund documents."
)


ADVICE_PATTERNS = (
    r"\bshould\s+i\s+(invest|buy|sell|hold|choose|switch|redeem)\b",
    r"\bshould\s+we\s+(invest|buy|sell|hold|choose|switch|redeem)\b",
    r"\b(can|could)\s+i\s+(invest|buy|sell|hold|choose|switch|redeem)\b",
    r"\bdo\s+you\s+recommend\b",
    r"\brecommend\s+(me|a|one|which)\b",
    r"\bwhich\b.*\b(better|best|good|suitable|choose)\b",
    r"\b(best|better|safest)\s+(fund|scheme)\b",
    r"\bgood\s+for\s+me\b",
    r"\bsuitable\s+for\s+me\b",
    r"\bbuy\s+or\s+sell\b",
    r"\binvest\s+or\s+not\b",
)


@dataclass(frozen=True)
class QuestionClassification:
    is_advice: bool
    reason: str
    refusal_response: str = REFUSAL_RESPONSE


def classify_question(question: str) -> QuestionClassification:
    normalized = " ".join(question.lower().split())

    for pattern in ADVICE_PATTERNS:
        if re.search(pattern, normalized):
            return QuestionClassification(
                is_advice=True,
                reason="Question asks for investment advice, recommendation, suitability, or buy/sell decision.",
            )

    return QuestionClassification(is_advice=False, reason="Question is allowed for factual retrieval.")
