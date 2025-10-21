"""Plugin registry for language handlers."""

from typing import Type

from brownfield.plugins.base import LanguageHandler


class UnsupportedLanguageError(Exception):
    """Raised when language handler not found."""

    pass


_handlers: dict[str, Type[LanguageHandler]] = {}


def register_handler(name: str):
    """
    Decorator to register a language handler.

    Usage:
        @register_handler('python')
        class PythonHandler(LanguageHandler):
            ...
    """

    def decorator(cls: Type[LanguageHandler]) -> Type[LanguageHandler]:
        _handlers[name] = cls
        return cls

    return decorator


def get_handler(language: str) -> LanguageHandler:
    """
    Get registered handler for language.

    Args:
        language: Language name (lowercase)

    Returns:
        Instantiated handler

    Raises:
        UnsupportedLanguageError: If language not registered
    """
    if language not in _handlers:
        raise UnsupportedLanguageError(f"No handler for {language}")
    return _handlers[language]()


def list_supported_languages() -> list[str]:
    """Return list of supported language names."""
    return list(_handlers.keys())
