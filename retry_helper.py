import time
import random


def call_with_retry(func, max_retries=4, base_delay=1.5, *args, **kwargs):
    """
    Calls `func(*args, **kwargs)`, retrying on 429/503-style errors
    with exponential backoff + jitter.

    Usage:
        response = call_with_retry(
            client.models.generate_content,
            model="gemini-flash-latest",
            contents=prompt
        )
    """

    last_error = None

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            error_text = str(e).lower()

            is_retryable = (
                "429" in error_text
                or "503" in error_text
                or "unavailable" in error_text
                or "rate limit" in error_text
                or "resource_exhausted" in error_text
            )

            if not is_retryable or attempt == max_retries - 1:
                raise

            last_error = e

            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"⚠️ Gemini call failed ({e}). Retrying in {delay:.1f}s... "
                  f"(attempt {attempt + 1}/{max_retries})")

            time.sleep(delay)

    raise last_error