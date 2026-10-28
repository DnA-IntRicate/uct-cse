"""
The startup screen: pick a project, watch it load, then hand over to the viewer.

Choosing a project builds a MainWindow immediately but keeps it hidden, so the
loading bar can follow the real bundle load instead of guessing at one. The
viewer only appears once its scene is on screen.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QProcess, QSettings, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from viewscope import config
from viewscope import window as wd
from viewscope.config import APP_NAME, ORG_NAME, Project
from viewscope.data import STAGE_COUNT, validate_required_files
from viewscope.dialogs import BuildBundleDialog
from viewscope.scene import PhotoMeshLoader

CARD_SPACING = 10

# The memory budgets the page offers. LOW stops at the simplified mesh, which
# is what the great bulk of a bundle's footprint is spent on. MEDIUM adds the
# photographed model, with its textures capped on the way in. HIGH takes that
# model exactly as it was shipped, textures at their own size. MEDIUM and HIGH
# are both cached, each under its own variant, so the slow parse is paid once
# per budget rather than once per open.
#
# The labels name the experience rather than the number of gigabytes behind it;
# what each one actually costs is on the button's tooltip, where it can be said
# in a full sentence.
QUALITY_LOW = "Low"
QUALITY_MEDIUM = "Medium"
QUALITY_HIGH = "High"

STYLESHEET = f"""
#startupPage {{
    background: {config.PAGE};
}}
#title {{
    color: {config.INK};
}}
#tagline {{
    color: {config.MUTED};
    font-size: 13px;
    letter-spacing: 1px;
}}
#sectionLabel {{
    color: {config.MUTED};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
}}
#hairline {{
    background: {config.HAIRLINE};
    border: none;
}}
#projectCard {{
    background: {config.CARD};
    border: 1px solid {config.CARD_BORDER};
    border-radius: 10px;
}}
#projectCard:hover {{
    background: {config.CARD_HOVER};
    border-color: {config.CARD_BORDER_HOVER};
}}
#projectCard:focus {{
    border-color: {config.ACCENT};
}}
#projectCard[busy="true"] {{
    background: {config.TRACK};
    border-color: {config.CARD_BORDER};
}}
#cardMark {{
    background: {config.TRACK};
    color: {config.ACCENT};
    border-radius: 8px;
    font-size: 19px;
    font-weight: 600;
}}
#cardName {{
    color: {config.INK};
    font-size: 15px;
    font-weight: 600;
}}
#cardSubtitle {{
    color: {config.MUTED};
    font-size: 12px;
}}
#cardChevron {{
    color: {config.ACCENT};
    font-size: 17px;
}}
#addCard {{
    background: transparent;
    border: 1px dashed {config.CARD_BORDER_HOVER};
    border-radius: 10px;
    color: {config.MUTED};
    font-size: 13px;
    min-height: 46px;
    text-align: left;
    padding-left: 21px;
}}
#addCard:hover {{
    background: {config.CARD};
    border-color: {config.ACCENT};
    color: {config.ACCENT};
}}
#qualityButton {{
    background: {config.CARD};
    border: 1px solid {config.CARD_BORDER};
    border-radius: 6px;
    color: {config.MUTED};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 4px 10px;
}}
#qualityButton:hover {{
    border-color: {config.CARD_BORDER_HOVER};
    color: {config.INK};
}}
#qualityButton:checked {{
    background: {config.TRACK};
    border-color: {config.ACCENT};
    color: {config.ACCENT};
}}
#linkButton {{
    background: transparent;
    border: none;
    color: {config.ACCENT};
    font-size: 12px;
    text-decoration: underline;
}}
#cardScroll, #cardHost {{
    background: transparent;
    border: none;
}}
#status {{
    color: {config.MUTED};
    font-size: 12px;
}}
QProgressBar {{
    background: {config.TRACK};
    border: none;
    border-radius: 3px;
}}
QProgressBar::chunk {{
    background: {config.ACCENT};
    border-radius: 3px;
}}
"""


@dataclass
class _Build:
    """The bundle a running builder process is writing, and what it has said."""

    name: str
    out_dir: Path
    log: list[str] = field(default_factory=list)


def wordmark_font() -> QFont:
    """A serif face for the title, whichever of these the platform has."""
    font = QFont()
    font.setFamilies(["Palatino", "Georgia", "Times New Roman"])
    font.setStyleHint(QFont.StyleHint.Serif)
    font.setPixelSize(58)
    font.setWeight(QFont.Weight.Medium)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
    return font


class ProjectCard(QFrame):
    """One project in the list. Clicking it, or pressing Return on it, opens it."""

    clicked = Signal(object)  # Project
    HEIGHT = 78

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setObjectName("projectCard")
        self.setFixedHeight(self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setProperty("busy", False)
        self._eliding = False

        row = QHBoxLayout(self)
        row.setContentsMargins(18, 16, 20, 16)
        row.setSpacing(16)

        mark = QLabel(project.name[:1].upper())
        mark.setObjectName("cardMark")
        mark.setFixedSize(46, 46)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(mark)

        text = QVBoxLayout()
        text.setSpacing(3)
        name = QLabel(project.name)
        name.setObjectName("cardName")
        self.subtitle = QLabel(project.subtitle)
        self.subtitle.setObjectName("cardSubtitle")
        # Ignored, so that a long subtitle asks the card for no extra width.
        self.subtitle.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        text.addWidget(name)
        text.addWidget(self.subtitle)
        row.addLayout(text, 1)

        self.chevron = QLabel("→")
        self.chevron.setObjectName("cardChevron")
        row.addWidget(self.chevron, 0, Qt.AlignmentFlag.AlignVCenter)

    # -- interaction ---------------------------------------------------

    def resizeEvent(self, event):
        """Keep a long subtitle, such as the path of an added bundle, inside the card."""
        super().resizeEvent(event)
        if self._eliding:
            return  # setting the text lays the card out again, which lands back here

        metrics = QFontMetrics(self.subtitle.font())
        elided = metrics.elidedText(
            self.project.subtitle, Qt.TextElideMode.ElideMiddle, self.subtitle.width()
        )
        if elided == self.subtitle.text():
            return

        self._eliding = True
        try:
            self.subtitle.setText(elided)
        finally:
            self._eliding = False

    def mouseReleaseEvent(self, event):
        inside = self.rect().contains(event.position().toPoint())
        if event.button() == Qt.MouseButton.LeftButton and inside:
            self.activate()
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.activate()
            return
        super().keyPressEvent(event)

    def activate(self):
        """Ask for this project, unless it is already opening."""
        if not self.property("busy"):
            self.clicked.emit(self.project)

    def set_busy(self, busy: bool):
        self.setProperty("busy", busy)
        self.chevron.setText("…" if busy else "→")
        self.setCursor(Qt.CursorShape.ArrowCursor if busy else Qt.CursorShape.PointingHandCursor)
        # Qt only re-reads property selectors when the style is refreshed.
        self.style().unpolish(self)
        self.style().polish(self)


class StartupWindow(QWidget):
    """The landing page: the wordmark above, the project list below."""

    VISIBLE_CARDS = 3

    def __init__(self, projects=config.PROJECTS, parent=None, settings=None):
        """projects are the bundles we ship; anything the user added is loaded on top."""
        super().__init__(parent)
        self.setObjectName("startupPage")
        self.setWindowTitle("Swapchain")
        self.setStyleSheet(STYLESHEET)
        self.setMinimumSize(680, 620)
        self.resize(880, 680)

        self.viewer = None  # the MainWindow being loaded, once a project is picked

        # Building the viewer blocks this thread, so it waits for the busy state
        # to paint. Owned by the window, so closing the page calls it off.
        self._pending_project = None
        self.builder: QProcess | None = None  # the QProcess of a running build, if any
        self._build: _Build | None = None  # what it is building
        self._open_timer = QTimer(self)
        self._open_timer.setSingleShot(True)
        self._open_timer.timeout.connect(self._start_pending_load)
        self.settings = settings if settings is not None else QSettings(ORG_NAME, APP_NAME)
        self.shipped = tuple(projects)
        self.projects = []

        page = QVBoxLayout(self)
        page.setContentsMargins(56, 48, 56, 40)
        page.setSpacing(0)

        title = QLabel("SWAPCHAIN⛓")
        title.setObjectName("title")
        title.setFont(wordmark_font())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tagline = QLabel("VIEWPOINT PLANNING STUDIO")
        tagline.setObjectName("tagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        page.addLayout(self._quality_toggle())
        page.addStretch(3)
        page.addWidget(title)
        page.addSpacing(12)
        page.addWidget(tagline)
        page.addStretch(4)

        page.addLayout(self._section_heading("PROJECTS"))
        page.addSpacing(16)
        page.addWidget(self._project_list())

        self.add_button = QPushButton("+   Add a project...")
        self.add_button.setObjectName("addCard")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setToolTip("Open a folder holding scene.obj, targets.ply, plan.json ...")
        self.add_button.clicked.connect(self.choose_project)

        self.build_button = QPushButton("+   Build a project from a model...")
        self.build_button.setObjectName("addCard")
        self.build_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.build_button.setToolTip("Turn an .obj into a bundle, then add it")
        self.build_button.clicked.connect(self.choose_model)

        page.addSpacing(10)
        page.addWidget(self.add_button)
        page.addSpacing(8)
        page.addWidget(self.build_button)

        page.addSpacing(16)
        page.addLayout(self._progress_row())

        self.cards = {}
        for project in (*self.shipped, *self._saved_projects()):
            self._add_card(project)
        self._fit_project_list()

    def _quality_toggle(self) -> QHBoxLayout:
        """The memory budget, in the top right corner. Full quality by default."""
        row = QHBoxLayout()
        row.setSpacing(6)
        row.addStretch(1)

        self.quality_group = QButtonGroup(self)
        self.quality_group.setExclusive(True)
        self.quality_buttons = {}

        cap = PhotoMeshLoader.MAX_TEXTURE_DIM
        tips = {
            QUALITY_LOW: config.tooltip(
                "Requires around 600MB",
                "The simplified planning mesh on its own. "
                "Every panel draws the shape of the site rather than the "
                "surface the survey photographed.",
            ),
            QUALITY_MEDIUM: config.tooltip(
                "Requires around 6GB",
                "Adds the photographed model and its textures capped at "
                f"{cap}px. The first open of a project parses it. Every open "
                "after that reads it back from the cache. "
                "This is ideal for laptops with 8GB RAM",
            ),
            QUALITY_HIGH: config.tooltip(
                "Requires around 10GB",
                "The photographed model exactly as it was shipped, textures at "
                "their own full size. The sharpest picture and the heaviest on "
                "the GPU. "
                "Ideal for high end computers",
            ),
        }
        for label in (QUALITY_LOW, QUALITY_MEDIUM, QUALITY_HIGH):
            button = QPushButton(label)
            button.setObjectName("qualityButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(tips[label])
            self.quality_group.addButton(button)
            self.quality_buttons[label] = button
            row.addWidget(button)

        self.quality_buttons[QUALITY_MEDIUM].setChecked(True)
        return row

    @property
    def load_photo_mesh(self) -> bool:
        """Whether a project opened now should read the full-resolution model."""
        return not self.quality_buttons[QUALITY_LOW].isChecked()

    @property
    def full_resolution_mesh(self) -> bool:
        """Whether that model should come in uncapped and uncached."""
        return self.quality_buttons[QUALITY_HIGH].isChecked()

    def _project_list(self) -> QScrollArea:
        """The cards, in a scroller so a long list cannot push the page apart."""
        self.card_host = QWidget()
        self.card_host.setObjectName("cardHost")
        self.card_column = QVBoxLayout(self.card_host)
        self.card_column.setContentsMargins(0, 0, 0, 0)
        self.card_column.setSpacing(CARD_SPACING)
        self.card_column.addStretch(1)  # cards sit at the top, at their own height

        self.card_scroll = QScrollArea()
        self.card_scroll.setObjectName("cardScroll")
        self.card_scroll.setWidget(self.card_host)
        self.card_scroll.setWidgetResizable(True)
        self.card_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.card_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.card_scroll.viewport().setAutoFillBackground(False)
        self.card_host.setAutoFillBackground(False)
        return self.card_scroll

    def _fit_project_list(self):
        """Hold the list at its content height, up to VISIBLE_CARDS, then scroll.

        A fixed height, because a stretchy one gets squeezed by the space the
        wordmark above it wants, and squeezed cards overlap.
        """
        rows = max(1, min(len(self.cards), self.VISIBLE_CARDS))
        self.card_scroll.setFixedHeight(rows * ProjectCard.HEIGHT + (rows - 1) * CARD_SPACING)

    def _section_heading(self, text: str) -> QHBoxLayout:
        """A small caps label trailed by a hairline across the rest of the width."""
        row = QHBoxLayout()
        row.setSpacing(14)

        label = QLabel(text)
        label.setObjectName("sectionLabel")
        row.addWidget(label)

        rule = QFrame()
        rule.setObjectName("hairline")
        rule.setFixedHeight(1)
        rule.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row.addWidget(rule, 1)
        return row

    def _progress_row(self) -> QVBoxLayout:
        column = QVBoxLayout()
        column.setSpacing(10)

        self.status = QLabel("Select a project to open it.")
        self.status.setObjectName("status")

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("linkButton")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.clicked.connect(self.cancel_build)
        self.cancel_button.hide()

        line = QHBoxLayout()
        line.addWidget(self.status, 1)
        line.addWidget(self.cancel_button)
        column.addLayout(line)

        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setRange(0, STAGE_COUNT)
        self.bar.setValue(0)
        # Keep the bar's space reserved so the cards do not jump when it appears.
        policy = self.bar.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.bar.setSizePolicy(policy)
        self.bar.hide()
        column.addWidget(self.bar)
        return column

    # -- the project list ----------------------------------------------

    def _add_card(self, project: Project):
        """Put a project on the page. Bundles the user added can be taken off again."""
        card = ProjectCard(project)
        card.clicked.connect(self.open_project)
        self.projects.append(project)
        self.cards[str(project.data_dir)] = card
        self.card_column.insertWidget(self.card_column.count() - 1, card)  # above the stretch

        if project not in self.shipped:
            card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            card.customContextMenuRequested.connect(
                lambda point, p=project: self._offer_removal(p, point)
            )
            card.setToolTip(f"{project.data_dir}\nRight click to take it off the list.")

        self._fit_project_list()
        return card

    def choose_project(self):
        """Ask for a bundle folder, and add it if it holds a bundle."""
        folder = QFileDialog.getExistingDirectory(self, "Choose a project folder", str(Path.home()))
        if folder:
            self.add_folder(Path(folder))

    def add_folder(self, folder: Path, name: str | None = None) -> bool:
        """Add the bundle in this folder to the list, or explain why it cannot be."""
        if any(Path(p.data_dir) == folder for p in self.projects):
            self.status.setText(f"{folder.name} is already on the list.")
            return False

        try:
            complete, message = validate_required_files(str(folder))
        except OSError as error:
            self.status.setText(f"Could not read {folder.name}: {error.strerror}")
            return False

        if not complete:
            self.status.setText(message)
            return False

        self._add_card(Project(name=name or folder.name, subtitle=str(folder), data_dir=folder))
        self._remember_added()
        self.status.setText(f"Added {name or folder.name}. Select it to open it.")
        return True

    # -- building a bundle from a model --------------------------------

    def choose_model(self):
        """Pick an .obj and, once the settings are confirmed, build a bundle from it."""
        if self.builder is not None:
            self.status.setText("A build is already running.")
            return

        model, _ = QFileDialog.getOpenFileName(
            self, "Choose a model", str(Path.home()), "Wavefront models (*.obj)"
        )
        if not model:
            return

        dialog = BuildBundleDialog(Path(model), self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.build_bundle(Path(model), dialog.settings())

    def build_bundle(self, model: Path, settings: dict):
        """Run the builder over this model, in a process of its own.

        Its renderer wants an OpenGL context, and the library asks for one live
        SceneRenderer per process, so it does not share this one.
        """
        out_dir = Path(settings["out_dir"])
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            self.status.setText(f"Cannot write to {out_dir}: {error.strerror}")
            return

        self._build = _Build(name=settings["name"], out_dir=out_dir)

        self.builder = QProcess(self)
        self.builder.setProgram(sys.executable)
        self.builder.setArguments(
            [
                "-u",  # unbuffered, so the stages arrive as they happen
                "-m",
                "viewscope.build_bundle",
                str(model),
                str(out_dir),
                "--length",
                str(settings["length"]),
                "--up",
                settings["up"],
                "--targets",
                str(settings["targets"]),
                "--viewpoints",
                str(settings["viewpoints"]),
            ]
        )
        self.builder.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.builder.readyReadStandardOutput.connect(self._on_build_output)
        self.builder.finished.connect(self._on_build_finished)
        self.builder.errorOccurred.connect(self._on_build_error)

        self.build_button.setEnabled(False)
        self.add_button.setEnabled(False)
        self.cancel_button.show()
        self.status.setText(f"Building {settings['name']}...")
        self.bar.setRange(0, 0)  # busy, until the first stage says how many there are
        self.bar.show()

        self.builder.start()

    def cancel_build(self):
        """Stop a running build. Whatever it wrote so far is left on disk."""
        if self.builder is None:
            return
        self.builder.kill()
        self.status.setText("Build cancelled.")

    def _on_build_output(self):
        """Follow the stage lines the builder prints, such as "[3/6] planning"."""
        if self.builder is None or self._build is None:
            return
        raw = self.builder.readAllStandardOutput().data()
        text = bytes(raw).decode("utf-8", "replace")
        for line in text.splitlines():
            if not line.strip():
                continue
            self._build.log.append(line)
            stage = re.match(r"^\[(\d+)/(\d+)\]\s*(.*)$", line.strip())
            if stage:
                done, total, message = stage.groups()
                self.bar.setRange(0, int(total))
                self.bar.setValue(int(done))
                self.status.setText(f"{self._build.name}: {message}")

    def _on_build_error(self, _error):
        message = self.builder.errorString() if self.builder is not None else "unknown error"
        self._finish_build(f"Could not run the builder: {message}")

    def _on_build_finished(self, exit_code, _status):
        if self._build is None:
            return

        if exit_code == 0:
            out_dir = self._build.out_dir
            name = self._build.name
            self._finish_build("")
            if self.add_folder(out_dir, name=name):
                self.status.setText(f"Built {name}. Select it to open it.")
            return

        if self.status.text() != "Build cancelled.":
            tail = next(
                (line for line in reversed(self._build.log) if line.strip()),
                "no output",
            )
            self._finish_build(f"Build failed: {tail}")
        else:
            self._finish_build(self.status.text())

    def _finish_build(self, message: str):
        if self.builder is not None:
            self.builder.deleteLater()
        self.builder = None
        self.cancel_button.hide()
        self.build_button.setEnabled(True)
        self.add_button.setEnabled(True)
        self.bar.setRange(0, STAGE_COUNT)
        self.bar.hide()
        if message:
            self.status.setText(message)

    def remove_project(self, project: Project):
        """Take an added project off the list. The bundle on disk is left alone."""
        card = self.cards.pop(str(project.data_dir), None)
        if card is None:
            return
        self.projects.remove(project)
        self.card_column.removeWidget(card)
        card.deleteLater()
        self._fit_project_list()
        self._remember_added()
        self.status.setText(f"Removed {project.name} from the list.")

    def _offer_removal(self, project: Project, point):
        menu = QMenu(self)
        menu.addAction("Remove from the list").triggered.connect(
            lambda _checked=False, p=project: self.remove_project(p)
        )
        menu.exec(self.cards[str(project.data_dir)].mapToGlobal(point))

    def _saved_projects(self) -> list[Project]:
        """Projects added on an earlier run, skipping any entry that no longer reads."""
        stored = self.settings.value("projects", "[]")
        try:
            entries = json.loads(stored) if isinstance(stored, str) else []
        except json.JSONDecodeError:
            entries = []

        projects = []
        for entry in entries if isinstance(entries, list) else []:
            try:
                projects.append(Project.from_dict(entry))
            except KeyError, TypeError:
                continue
        return projects

    def _remember_added(self):
        """Save the added projects, so the next run starts with them."""
        added = [p.as_dict() for p in self.projects if p not in self.shipped]
        self.settings.setValue("projects", json.dumps(added))

    # -- Opening a project ---------------------------------------------

    def open_project(self, project: Project):
        if self.viewer is not None:
            return  # already opening one

        if self.builder is not None:
            name = self._build.name if self._build is not None else "a project"
            self.status.setText(f"Building {name}; cancel it or let it finish.")
            return

        self.cards[str(project.data_dir)].set_busy(True)
        self.status.setText(f"Opening {project.name}...")

        self.bar.setRange(0, STAGE_COUNT)
        self.bar.setValue(0)
        self.bar.show()
        self.add_button.setEnabled(False)
        self._enable_quality(False)

        self._pending_project = project
        self._open_timer.start(0)

    def _start_pending_load(self):
        project, self._pending_project = self._pending_project, None
        if project is not None:
            self._start_load(project)

    def _start_load(self, project: Project):
        viewer = wd.MainWindow(
            project.data_dir,
            expected_viewpoints=project.expected_viewpoints,
            defer_load=True,
            load_photo_mesh=self.load_photo_mesh,
            full_resolution_mesh=self.full_resolution_mesh,
        )
        self.viewer = viewer

        viewer.back_requested.connect(self.show_projects)

        loader = viewer.loader
        loader.progress.connect(self.status.setText)
        loader.stage.connect(self._on_stage)
        loader.failed.connect(self._on_failed)
        loader.loaded.connect(self._on_scene_loaded)

        # The photo-mesh load starts itself from inside the viewer's own
        # scene-loaded handler.
        viewer.photo_mesh_progress.connect(self._on_photo_mesh_progress)
        viewer.photo_mesh_finished.connect(self._on_photo_mesh_finished)

        loader.start()

    def _on_stage(self, started: int, total: int):
        self.bar.setRange(0, total)
        self.bar.setValue(started)

    def _on_scene_loaded(self, _scene: object | None = None):
        """
        The scene itself is ready, but the window stays hidden: a
        full-resolution model may still be streaming in behind it. Switch the
        bar to percentage mode for that second phase rather than reveal the
        viewer while it's still loading textures.

        On the light budget there is no second phase - the viewer is already on
        its way up by the time this runs - so the bar is left as it is.
        """
        if not self.load_photo_mesh:
            return

        self.status.setText("Loading full-resolution model...")
        self.bar.setRange(0, 100)
        self.bar.setValue(0)

    def _on_photo_mesh_progress(self, message: str, percent: int):
        self.status.setText(message)
        self.bar.setValue(percent)

    def _on_photo_mesh_finished(self, _loaded: bool):
        self._run_viewer(None)

    def _run_viewer(self, _scene):
        viewer = self.viewer
        if viewer is None:
            return

        self.bar.setValue(self.bar.maximum())
        self.status.setText("Ready")

        viewer.show()
        viewer.raise_()
        viewer.activateWindow()
        viewer.start()
        self.hide()  # After the viewer is up, so the application keeps a window

    def show_projects(self):
        """Come back from the viewer to the project list, and let the bundle go."""
        viewer, self.viewer = self.viewer, None

        # Shown before the viewer closes, so the application is never without a
        # window and never quits on its own.
        self.show()
        self.raise_()
        self.activateWindow()

        if viewer is not None:
            viewer.close()  # saves its layout, stops its loader, releases VTK
            viewer.deleteLater()

        self._reset_page("Select a project to open it.")

    def _enable_quality(self, enabled: bool):
        """The budget is read when a project opens, so it is frozen while one does."""
        for button in self.quality_buttons.values():
            button.setEnabled(enabled)

    def _reset_page(self, message: str):
        """Put the page back the way it looks before anything was picked."""
        for card in self.cards.values():
            card.set_busy(False)
        self.add_button.setEnabled(True)
        self._enable_quality(True)
        self.build_button.setEnabled(self.builder is None)
        self.bar.hide()
        self.status.setText(message)

    def _on_failed(self, _message):
        # The viewer has already reported the failure in its own dialog. Put the
        # page back the way it was so the project can be tried again.
        viewer, self.viewer = self.viewer, None
        if viewer is not None:
            viewer.close()
            viewer.deleteLater()

        self._reset_page("Could not open the project. Select it to try again.")

    def closeEvent(self, event):
        self._open_timer.stop()
        self._pending_project = None
        if self.builder is not None:
            self.builder.kill()
            self.builder.waitForFinished(2000)

        viewer = self.viewer
        if viewer is not None and not viewer.isVisible():
            # Closed mid-load: let the viewer shut its loader thread down.
            self.viewer = None
            viewer.close()
        super().closeEvent(event)
