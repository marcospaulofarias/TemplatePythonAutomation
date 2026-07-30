import pytest
from resources.Browser import Browser


class FakeElement:
    def __init__(self):
        self.value = ""
        self.cleared = False
        self.keys = []

    def clear(self):
        self.cleared = True
        self.value = ""

    def send_keys(self, caract):
        self.keys.append(caract)
        self.value += caract

    def get_attribute(self, name):
        if name == "value":
            return self.value
        return None


class FakePrintAutomation:
    def print_error(self, *args, **kwargs):
        return None


class FakeBrowser(Browser):
    def __init__(self):
        # not calling super().__init__ to avoid side effects
        self.printautomation = FakePrintAutomation()
        self.driver = None


def test_keyboard_fills_value_and_returns():
    browser = FakeBrowser()
    element = FakeElement()

    browser.keyboard(
        element=element,
        word="abc123",
        key_down=False,
        just_numbers=False,
        verify=True,
        clean=True,
        max_attempts=2,
    )

    assert element.value == "abc123"
    assert element.cleared is True


def test_keyboard_raises_after_failed_attempts(monkeypatch):
    browser = FakeBrowser()
    element = FakeElement()

    def bad_send_keys(caract):
        element.value = "bad"

    element.send_keys = bad_send_keys

    with pytest.raises(RuntimeError, match="Não foi possível preencher o campo corretamente"):
        browser.keyboard(
            element=element,
            word="abc123",
            key_down=False,
            just_numbers=False,
            verify=True,
            clean=True,
            max_attempts=2,
        )
