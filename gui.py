from abc import abstractmethod
from typing import Optional
from anki.notes import Note, NoteId
from aqt import AnkiQt
from aqt.qt import *

class TopologyDialog(QMainWindow):
    def __init__(
        self, fields: dict[str, str],
        note_id: Optional[NoteId], topo: "NoteTopology"
    ):
        super().__init__(topo.mw)
        self.mw = topo.mw
        self.fields = fields
        self.note_id = note_id
        self.topo = topo
        self.setWindowTitle(topo.description() + " view")

        central = QWidget()
        self.setCentralWidget(central)
        outer_layout = QVBoxLayout(central)
        self.build_interface(outer_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer_layout.addWidget(buttons)

    @abstractmethod
    def build_interface(self, layout: QBoxLayout) -> None:
        pass

    @abstractmethod
    def capture_fields(self) -> None:
        pass

    def accept(self) -> None:
        self.capture_fields()
        col = self.mw.col
        if self.note_id:
            note = col.get_note(self.note_id)
            old_note_size = len(note.values())
            if len(self.fields) != old_note_size:
                self.topo.enlarge_note(note, self.topo.measure_order(
                    self.fields
                ))
                note = col.get_note(self.note_id)
            for k, v in self.fields.items():
                note[k] = v
            col.update_note(note)
        else:
            order = self.topo.measure_order(self.fields)
            name = self.topo.model_name(order)
            model = col.models.by_name(name)
            if model is None:
                col.models.add_dict(self.topo.make_model(order))
                model = col.models.by_name(name)
            note = col.new_note(model)
            for k, v in self.fields.items():
                note[k] = v
            col.add_note(note, col.decks.current()["id"])
        self.close()

    def reject(self) -> None:
        self.close()
