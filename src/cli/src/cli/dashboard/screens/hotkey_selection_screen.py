from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, SelectionList
from textual.containers import Container, Horizontal
from textual.binding import Binding
from textual.widgets.selection_list import Selection


from cli.utils.config import Config
from cli.utils.wallet import get_all_hotkeys


class HotkeySelectionScreen(ModalScreen[list[str]]):
    """Screen for selecting hotkeys to filter by."""

    CSS = """
    HotkeySelectionScreen {
        align: center middle;
        background: $background 80%;
    }

    #dialog {
        width: 60;
        height: 80%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #hotkey_list {
        height: 1fr;
        border: solid $secondary;
        margin-bottom: 1;
    }

    #buttons {
        height: auto;
        align: center bottom;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("n", "cancel", "No"),
        Binding("enter", "confirm", "Confirm"),
        Binding("y", "confirm", "Yes"),
    ]

    def __init__(self, selected_hotkeys: list[str] | None = None) -> None:
        super().__init__()
        self.initial_selection = selected_hotkeys or []

    def compose(self) -> ComposeResult:
        config = Config.load_config()
        if not config.wallet_path:
            return
        all_hotkeys = get_all_hotkeys(config.wallet_path)
            
        # Sort hotkeys by wallet name then hotkey name
        all_hotkeys.sort(key=lambda x: (x["wallet_name"], x["hotkey_name"]))

        # Create selection items
        items = []
        for info in all_hotkeys:
            label = f"{info['wallet_name']} / {info['hotkey_name']} ({info['ss58_address'][:8]}...)"
            value = info["ss58_address"]
            items.append(Selection(label, value, value in self.initial_selection))

        with Container(id="dialog"):
            yield Label("Select Hotkeys to Track", id="title")
            yield SelectionList(*items, id="hotkey_list")
            with Horizontal(id="buttons"):
                yield Button(r"\[N]o", variant="error", id="cancel")
                yield Button(r"\[Y]es", variant="success", id="confirm")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.action_confirm()
        else:
            self.action_cancel()

    def action_confirm(self) -> None:
        selection_list = self.query_one("#hotkey_list", SelectionList)
        self.dismiss(selection_list.selected)

    def action_cancel(self) -> None:
        self.dismiss(None)
