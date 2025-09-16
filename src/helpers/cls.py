from inspect import getmembers, isfunction


def get_all_methods[T](cls: T, include_magic: bool = False) -> set[str]:
    """
    Возвращает множество имен методов класса.

    Args:
        cls: Класс, методы которого нужно извлечь.
        include_magic: Если True, включает магические методы (начинающиеся с '__').

    Returns:
        Множество имен методов класса.
    """
    methods = getmembers(cls, predicate=isfunction)
    return {
        name
        for name, _ in methods
        if include_magic or not name.startswith("__")
    }


def check_sub_class(cls: type, base: type, is_raise: bool = True) -> bool:
    if issubclass(cls, base):
        return True
    if is_raise:
        raise SubclassError(f"{cls.__name__} must inherit from {base.__name__}")
    return False


class SubclassError(TypeError):
    """Error raised when a class does not inherit from the required base class."""

    ...
