from aiogram import html


def split_text_with_wrap(text: str, max_length: int = 250) -> list[str]:
    if not text:
        return []

    if max_length < 1:
        raise ValueError("max_length must be positive")

    lines = text.splitlines()
    result = []
    current_message = ""

    for line in lines:
        if len(current_message) + len(line) + 1 <= max_length:
            # Если добавление строки не превышает лимит, добавляем её
            current_message += (line + "\n")
        else:
            # Если лимит превышается, сохраняем текущее сообщение и начинаем новое
            result.append(current_message.strip())
            current_message = line + "\n"

    # Добавляем последнее сообщение, если оно не пустое
    if current_message.strip():
        result.append(current_message.strip())

    return result


def quote_html(text: str | None) -> str | None:
    if text is None:
        return None
    return html.quote(text)


def quote_html_range(texts: list[str | None]) -> tuple[str | None]:
    return (quote_html(text) for text in texts)
