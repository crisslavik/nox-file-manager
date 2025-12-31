# integrations/substance_painter/init.py
"""
Substance Painter integration initialization
"""

try:
    from .nox_file_dialog_substance_painter import initialize_substance_painter_integration
    
    # Initialize NOX integration when Substance Painter starts
    initialize_substance_painter_integration()
    
except ImportError as e:
    print(f"Could not initialize Substance Painter integration: {e}")
