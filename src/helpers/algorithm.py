def get_key(input_dict: dict, target_value):
    for key, value in input_dict.items():
        if value == target_value:
            return key
    raise ValueError(f"{target_value} не найден в {input_dict}")
