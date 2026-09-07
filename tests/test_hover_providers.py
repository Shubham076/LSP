from __future__ import annotations

from LSP.plugin import HoverContentProvider
from LSP.plugin import Promise
from LSP.plugin import register_hover_content_provider
from LSP.plugin import unregister_hover_content_provider
from LSP.plugin.core.hover_providers import hover_content_providers
import sublime
import unittest


def make_provider(content: str | None) -> HoverContentProvider:
    def provider(_view: sublime.View, _point: int) -> Promise[str | None]:
        return Promise.resolve(content)
    return provider


class HoverContentProvidersTests(unittest.TestCase):

    def tearDown(self) -> None:
        for name, _, _ in hover_content_providers():
            unregister_hover_content_provider(name)

    def test_no_providers_by_default(self) -> None:
        self.assertEqual(hover_content_providers(), [])

    def test_register_and_unregister(self) -> None:
        register_hover_content_provider('Debugger', make_provider('debug'))
        self.assertEqual([name for name, _, _ in hover_content_providers()], ['Debugger'])
        unregister_hover_content_provider('Debugger')
        self.assertEqual(hover_content_providers(), [])

    def test_unregister_unknown_name_is_noop(self) -> None:
        unregister_hover_content_provider('DoesNotExist')

    def test_registering_twice_overwrites(self) -> None:
        register_hover_content_provider('Debugger', make_provider('first'))
        register_hover_content_provider('Debugger', make_provider('second'))
        providers = hover_content_providers()
        self.assertEqual(len(providers), 1)
        resolved: list[str | None] = []
        providers[0][2](sublime.View(0), 0).then(resolved.append)
        self.assertEqual(resolved, ['second'])

    def test_ordered_by_priority_then_name(self) -> None:
        register_hover_content_provider('C', make_provider('c'), priority=10)
        register_hover_content_provider('B', make_provider('b'))
        register_hover_content_provider('A', make_provider('a'), priority=-10)
        self.assertEqual([(name, priority) for name, priority, _ in hover_content_providers()],
                         [('A', -10), ('B', 0), ('C', 10)])
