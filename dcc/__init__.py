"""NOX File Manager DCC Module"""

# Import all DCC file managers
from .nuke_file_manager import NukeFileManager
from .houdini_file_manager import HoudiniFileManager
from .maya_file_manager import MayaFileManager
from .blender_file_manager import BlenderFileManager
from .mocha_file_manager import MochaFileManager
from .silhouette_file_manager import SilhouetteFileManager
from .equalizer_file_manager import EqualizerFileManager
from .substance_painter_file_manager import SubstancePainterFileManager

__all__ = [
    'NukeFileManager',
    'HoudiniFileManager',
    'MayaFileManager',
    'BlenderFileManager',
    'MochaFileManager',
    'SilhouetteFileManager',
    'EqualizerFileManager',
    'SubstancePainterFileManager'
]