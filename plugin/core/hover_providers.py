from __future__ import annotations

from .logging import debug
from typing import Callable
from typing import TYPE_CHECKING
import sublime

if TYPE_CHECKING:
    from .promise import Promise

# A callable that is given a view and a point in that view, and resolves to a minihtml fragment to be
# included in the hover popup, or to None to contribute nothing for that point.
HoverContentProvider = Callable[[sublime.View, int], 'Promise[str | None]']

_hover_content_providers: dict[str, tuple[int, HoverContentProvider]] = {}


def register_hover_content_provider(name: str, provider: HoverContentProvider, priority: int = 0) -> None:
    """
    Register a provider of additional content for the hover popup.

    The content of all registered providers is requested in parallel with the textDocument/hover requests
    and is merged into the same popup. A provider which resolves later than the others causes the visible
    popup to be updated, rather than a second popup to be shown.

    Contributed fragments can contain `subl:` links created with `make_command_link`, which allows a
    provider to offer interactive content without LSP having to route the callbacks.

    :param name: A unique name for the provider. Registering a name twice overwrites the first provider.
    :param priority: Providers are ordered by ascending priority, then by name. Content of providers with
                     a negative priority is placed above the content from the language servers.
    """
    if name in _hover_content_providers:
        debug(f'Hover content provider "{name}" is already registered. Overwriting.')
    _hover_content_providers[name] = (priority, provider)


def unregister_hover_content_provider(name: str) -> None:
    """Unregister the hover content provider with the given name. Unknown names are ignored."""
    _hover_content_providers.pop(name, None)


def hover_content_providers() -> list[tuple[str, int, HoverContentProvider]]:
    """Registered providers as (name, priority, provider), ordered by ascending priority, then by name."""
    return [
        (name, priority, provider)
        for name, (priority, provider) in sorted(
            _hover_content_providers.items(), key=lambda item: (item[1][0], item[0]))
    ]
