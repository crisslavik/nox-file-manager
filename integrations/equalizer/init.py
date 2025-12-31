# integrations/equalizer/init.py
"""
3DEqualizer integration initialization
"""

try:
    from .nox_file_dialog_equalizer import initialize_equalizer_integration
    
    # Initialize NOX integration when 3DEqualizer starts
    initialize_equalizer_integration()
    
except ImportError as e:
    print(f"Could not initialize 3DEqualizer integration: {e}")
