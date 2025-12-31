# NOX File Manager UI Overview

This document explains what each region of the NOX File Manager UI represents, what changes between **Load** vs **Save** modes, and what is expected to differ per DCC (Maya/Nuke/Houdini/Blender/etc.).

The UI exists in two forms:

- `ui/prototype.html`: HTML prototype used for layout/UX iteration.
- `ui/file_dialog.py`: the real shared Qt (PySide6) dialog used by all DCC integrations.

---

## 1) Top Bar / Header

### **Purpose**
- Identifies the dialog context (NOX + Load/Save + DCC name).
- Hosts window controls (close/minimize) in the prototype.

### **Load vs Save**
- **Load**: title indicates loading/opening into the current DCC.
- **Save**: title indicates saving/exporting from the current DCC.

### **DCC differences**
- Some DCCs embed this dialog into their native main window (parenting differs), but the UI content is the same.

---

## 2) Pipeline Context / Navigation Controls

(Shown as dropdowns in the prototype)

### **Purpose**
Select the pipeline “context” that drives:
- Where files are browsed from.
- How naming/versioning rules are applied.
- Which task/department is implied.

Typical levels:
- Show / Episode / Sequence / Shot (or Asset)
- Task (Comp, Animation, Lighting, etc.)

### **Load vs Save**
- **Load**: context determines which published/work files are shown as candidates to open/import/reference.
- **Save**: context determines the target folder and default filename pattern (shot/asset + task + version).

### **DCC differences**
- Context sources differ (ShotGrid, environment variables, local project config, etc.).
- Some DCCs can auto-detect context from the currently-open scene; others require manual selection.

---

## 3) Search + Filter Bar

### **Purpose**
- Search narrows visible items by name.
- Filter restricts by file extension/type.

### **Load vs Save**
- **Load**: filter helps you find compatible scene/script files.
- **Save**: filter typically matters less (saving usually targets a single extension), but it can still be useful for browsing versions.

### **DCC differences**
- Each DCC has different supported extensions:
  - Maya: `.ma`, `.mb`
  - Nuke: `.nk`
  - Houdini: `.hip`, `.hiplc`, `.hipnc`
  - Blender: `.blend`
  - etc.

---

## 4) File List (Table)

In the prototype and Qt dialog, the file list is a table with columns:

- **Name**: filename
- **Task**: pipeline task/department (Comp/Animation/etc.)
- **Version**: extracted from filename (e.g. `v004`)
- **Size**: file size
- **Updated**: last modified timestamp

### **Why no “Directory” column**
Directories are already visually distinct in the list and are navigated by double-click. A dedicated “Directory” column is redundant.

### **Why remove “.. (up)” and “publish”**
- The UX focus is pipeline-context browsing, not freeform filesystem navigation.
- “..” encourages escaping the context.
- “publish” is usually a controlled output area; whether it is browseable is pipeline-specific. In the prototype we removed it to match the intended workflow.

### **Load vs Save**
- **Load**: list shows candidate files to open/import/reference.
- **Save**: list is commonly used to review existing versions before saving a new one.

### **DCC differences**
- The *actions triggered* by selecting/double-clicking a row differ per DCC (see section 7).
- Metadata/preview availability differs depending on the DCC and file type.

---

## 5) Details Panel: File Information

### **Purpose**
Shows details for the currently-selected file:
- Name + full path
- Size
- Updated/Modified date
- Version
- Additional metadata (frame range, FPS, user, etc.) when available

### **Load vs Save**
- **Load**: information is about the file you’re about to load.
- **Save**: information is about the currently selected existing version (useful for comparing before you save a new version).

### **DCC differences**
- Some DCCs can read richer metadata from their file formats.
- For others, metadata is collected via sidecar files (e.g. `.meta.json`) or inferred from naming.

---

## 6) Preview Panel

### **Purpose**
Shows a thumbnail/preview when available.

### **Load vs Save**
- **Load**: preview helps confirm you are loading the correct file.
- **Save**: preview may show last saved/published thumbnail (or the current scene preview if generated).

### **DCC differences**
- Preview generation varies:
  - Maya/Blender can generate playblast/viewport thumbnails.
  - Nuke can capture viewer frame.
  - Houdini can capture viewport or flipbook.
  - Some applications may not support thumbnail generation via Python without additional tooling.

---

## 7) Options Panel (Load Mode / Save Options)

### **Load mode (Load dialog)**
Expected modes:
- **Open**: replace the current scene/script.
- **Import**: import/merge contents into current scene.
- **Reference**: reference/link (where supported).

**DCC differences (Load mode semantics):**
- **Maya**
  - Open: `cmds.file(open=True, force=True)`
  - Import: `cmds.file(i=True)`
  - Reference: `cmds.file(reference=True)`
- **Nuke**
  - Open: `nuke.scriptOpen()`
  - Import: `nuke.nodePaste()` (or script import pattern)
  - Reference: not a direct concept; can be implemented as “read nodes from script” depending on pipeline rules
- **Houdini**
  - Open: `hou.hipFile.load()`
  - Import: `hou.hipFile.merge()`
  - Reference: depends (USD/LOP workflows may treat references differently)
- **Blender**
  - Open: `bpy.ops.wm.open_mainfile()`
  - Import/Link: `bpy.ops.wm.append()` / `bpy.ops.wm.link()`

### **Save options (Save dialog)**
Common toggles:
- Create backup before saving
- Increment version automatically
- Validate before save
- Save metadata sidecar

**DCC differences (Save behavior):**
- Some DCCs support “incremental save” natively; others need pipeline logic.
- Scene dependency management differs (textures, caches, references).

---

## 8) Action Buttons

### **Load dialog**
- Primary: **Load** (or Open/Import/Reference depending on chosen mode)
- Secondary: Cancel

### **Save dialog**
- Primary: **Save** (or Save As)
- Secondary: Cancel

### **DCC differences**
- Confirmation dialogs differ (e.g., Maya prompts for unsaved changes).
- Some DCCs require main-thread execution or specific API contexts.

---

## 9) What is shared vs DCC-specific

### **Shared (same everywhere)**
- Layout and widgets (Qt dialog)
- Column definitions and selection handling
- Search/filter behavior
- Basic metadata display + preview placeholder

### **DCC-specific (varies)**
- How the dialog is launched and parented
- Supported extensions
- Load modes implementation
- Save/export implementation
- Metadata collection and thumbnail generation

---

## 10) File naming expectations (pipeline convention)

A common pattern used by NOX is:

`<entity>_<task>_v###.<ext>`

Examples:
- `SH0010_comp_v004.ma`
- `CharacterHero_model_v012.blend`

The UI uses this for:
- Extracting **Version**
- Inferring **Task** (fallback)

---

## Notes for implementation

- The HTML prototype is a UX reference; the Qt dialog (`ui/file_dialog.py`) is the authoritative implementation.
- Column alignment and content is centralized in the Qt dialog so that all DCCs remain consistent.
