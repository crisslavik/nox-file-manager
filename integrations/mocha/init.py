# integrations/mocha/init.py
"""
Mocha Pro integration initialization
"""

try:
    from .nox_file_dialog_mocha import initialize_mocha_integration
    
    # Initialize NOX integration when Mocha starts
    initialize_mocha_integration()
    
except ImportError as e:
    print(f"Could not initialize Mocha integration: {e}")
