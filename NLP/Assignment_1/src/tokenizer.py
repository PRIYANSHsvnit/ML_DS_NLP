import re

# Sentence Tokenizer

def sentence_tokenizer(text: str):
    """
    Splits a paragraph into sentences.

    Handles:
    .   !   ?   ।   ॥
    """

    if not text:
        return []

    text = text.strip()

    # Sentence-ending punctuation followed by whitespace
    pattern = r'(?<=[.!?।॥])\s+'

    sentences = re.split(pattern, text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# Word Tokenizer

TOKEN_PATTERN = re.compile(
    # URL
    r'https?://[^\s]+'

    # WWW URL
    r'|www\.[^\s]+'

    # Email
    r'|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'

    # Date: 15/08/2026, 15-08-2026
    r'|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'

    # Decimal number: 10.5
    r'|\d+\.\d+'

    # Integer
    r'|\d+'

    # English words
    r'|[A-Za-z]+'

    # Hindi / Devanagari words
    # Includes Devanagari letters and combining marks
    # without treating danda punctuation as part of a word.
    r'|(?:'
        r'[\u0904-\u0939\u0958-\u0961]'
        r'|[\u0900-\u0903\u093A-\u094D\u0951-\u0957\u0962-\u0963]'
    r')+'

    # Any remaining non-whitespace character = punctuation/symbol
    r'|[^\s]'
)


def word_tokenizer(sentence: str):
    """
    Tokenizes a sentence.

    Handles:
    - Hindi words
    - English words
    - URLs
    - Email IDs
    - Dates
    - Decimal numbers
    - Integers
    - Punctuation
    - Symbols
    """

    if not sentence:
        return []

    return TOKEN_PATTERN.findall(sentence)