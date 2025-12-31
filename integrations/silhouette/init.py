# integrations/silhouette/init.py
"""
Silhouette integration initialization
"""

try:
    from .nox_file_dialog_silhouette import initialize_silhouette_integration
    
    # Initialize NOX integration when Silhouette starts
    initialize_silhouette_integration()
    
except ImportError as e:
    print(f"Could not initialize Silhouette integration: {e}")
