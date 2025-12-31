# NOX VFX File Manager

A unified file management system for VFX studios, providing consistent load/save operations across multiple DCC applications.

## Features

- 🎨 **Unified Qt6 Interface** - Consistent UI across all DCCs
- 📁 **Smart File Management** - Auto-versioning, backups, metadata tracking
- 🔄 **Open vs Import Modes** - Choose how files are loaded
- 🎬 **Multi-DCC Support** - Nuke, Houdini, Maya, Blender, and more
- 🔌 **ShotGrid Integration** - Ready for pipeline integration
- 📊 **Metadata Tracking** - Detailed file information and history

## Supported Applications

- Foundry Nuke 16
- SideFX Houdini
- Autodesk Maya
- Blender
- Mocha Pro
- Silhouette
- 3DEqualizer
- Substance Painter

## Installation

### Quick Install
```bash
git clone https://github.com/noxvfx/nox-file-manager.git
cd nox-file-manager
python install.py
```

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the installer:
```bash
python install.py
```

3. Follow the prompts to select which DCCs to install for

## Usage

### In Nuke
```python
# Access via NOX menu
NOX > File > Load...
NOX > File > Save As...
```

### In Maya
```python
# Access via NOX menu
NOX > Load...
NOX > Save As...
```

### In Blender
```python
# Enable addon in Edit > Preferences > Add-ons
# Access via NOX panel in 3D Viewport (N key)
```

### In Houdini
```python
# Access via shelf or python
import nox_houdini
nox_houdini.show_load_dialog()
```

## Configuration

Edit `config/nox_pipeline.yaml`:
```yaml
project_root: /mnt/projects
file_manager:
  auto_version: true
  backup_enabled: true
  backup_count: 5
```

## Development

### Project Structure
```
nox-file-manager/
├── core/           # Core file management logic
├── ui/             # Qt6 user interface
├── dcc/            # DCC-specific implementations
├── integrations/   # DCC integration code
├── config/         # Configuration files
└── tests/          # Unit tests
```

### Running Tests
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Contact

NOX VFX - [cristian@noxvfx.com](mailto:cristian@noxvfx.com)

Project Link: [https://github.com/noxvfx/nox-file-manager](https://github.com/noxvfx/nox-file-manager)