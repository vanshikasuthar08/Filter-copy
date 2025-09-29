import re

# This is a simple date finder. It can be improved to find more formats.
DATE_PATTERN = re.compile(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4})\b')

# Finds amounts with currency symbols like $ or ₹
AMOUNT_PATTERN = re.compile(r'([$₹€£] ?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)')

# Finds common Purchase Order number formats
PO_NUMBER_PATTERN = re.compile(r'\b(?:PO|Order|Purchase Order)[\s#:]*([A-Z0-9-]+)\b', re.IGNORECASE)


def extract_entities(text: str) -> dict:
    """Finds all entities in a given text and returns them in a dictionary."""
    dates = DATE_PATTERN.findall(text)
    amounts = AMOUNT_PATTERN.findall(text)
    po_numbers = PO_NUMBER_PATTERN.findall(text)

    return {
        "dates": list(set(dates)), # Use set to get unique values
        "amounts": list(set(amounts)),
        "po_numbers": list(set(po_numbers))
    }