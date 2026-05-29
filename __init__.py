from abc import abstractmethod
from collections.abc import Iterable
import re
from typing import Optional

from anki.models import TemplateDict, NotetypeDict
from anki.notes import Note, NoteId
import aqt
from aqt.qt import *

from .gui import TopologyDialog

def indices(n: int) -> Iterable[int]:
    return range(1, n + 1)

class NoteTopology:
    def __init__(self, mw: aqt.AnkiQt) -> None:
        self.mw = mw
        edit_action = QAction("Edit " + self.description(), mw)
        edit_action.triggered.connect(lambda: self.browse_selected())
        mw.form.menuTools.addAction(edit_action)

    @staticmethod
    @abstractmethod
    def description() -> str:
        pass

    @classmethod
    def note_fits(cls, note: Note) -> Optional[int]:
        notetype = note.note_type()
        assert notetype is not None
        m = re.match(cls.description() + " \\[(\\d+)\\]", notetype["name"])
        return int(m.group(1)) if m else 0

    @classmethod
    def model_name(cls, order: int) -> str:
        return f"{cls.description()} [{order}]"

    @abstractmethod
    def make_templates(self, order: int) -> Iterable[TemplateDict]:
        pass

    @staticmethod
    @abstractmethod
    def make_fields(order: int) -> Iterable[str]:
        pass

    def custom_css(self, order: int) -> str:
        return ""

    def make_model(self, order: int) -> NotetypeDict:
        manager = self.mw.col.models
        model = manager.new(self.model_name(order))
        for template in self.make_templates(order):
            manager.add_template(model, template)
        for field in self.make_fields(order):
            manager.add_field(model, manager.new_field(field))
        model["css"] = (model["css"].replace("arial", "sans-serif") +
            "\n" + self.custom_css(order))
        return model

    def enlarge_note(self, note: Note, new_order: int) -> None:
        models = self.mw.col.models
        name = self.model_name(new_order)
        new_model = models.by_name(name)
        if new_model is None:
            models.add_dict(self.make_model(new_order))
            new_model = models.by_name(name)
        assert new_model is not None
        info = models.change_notetype_info(
            old_notetype_id=note.mid,
            new_notetype_id=new_model["id"]
        )
        info.input.note_ids.extend([note.id])
        models.change_notetype_of_notes(info.input)

    @staticmethod
    @abstractmethod
    def next_order(order: Optional[int] = None) -> int:
        pass

    @staticmethod
    @abstractmethod
    def measure_order(fields: dict[str, str]) -> int:
        pass

    @classmethod
    def blank_example(cls) -> dict[str, str]:
        return {field: "" for field in cls.make_fields(cls.next_order())}

    @abstractmethod
    def make_editor(
        self, fields: dict[str, str], note_id: Optional[NoteId]
    ) -> TopologyDialog:
        pass

    def browse_selected(self) -> None:
        col = self.mw.col
        browser = aqt.dialogs._dialogs.get("Browser", [None, None])[1]
        fields: Optional[dict[str, str]] = None
        note_id: Optional[NoteId] = None
        if browser:
            nids = browser.selected_notes()
            if nids:
                note = col.get_note(nids[0])
                assert note is not None
                if self.note_fits(note):
                    fields = dict(note.items())
                    note_id = nids[0]
        if not fields:
            fields = self.blank_example()
        editor = self.make_editor(fields, note_id)
        editor.setWindowState(Qt.WindowState.WindowMaximized)
        editor.showMaximized()
