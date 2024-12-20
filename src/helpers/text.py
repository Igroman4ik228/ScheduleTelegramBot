def split_text_with_wrap(text: str, max_length: int = 150) -> list[str]:
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
