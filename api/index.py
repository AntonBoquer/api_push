# Vercel entry point
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import from the root
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from main import app
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback: try importing with explicit path
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", parent_dir / "main.py")
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    app = main_module.app

# This is the entry point for Vercel
handler = app
