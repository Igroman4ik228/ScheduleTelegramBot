def add_html_tag(text: str, tag: str, attributes: dict = None) -> str:
    if attributes:
        attributes_tag = ' '.join(
            [f'{k}="{v}"' for k, v in attributes.items()]
        )
        return f"<{tag} {attributes_tag}>{text}</{tag}>"

    return f"<{tag}>{text}</{tag}>"
