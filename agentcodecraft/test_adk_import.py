"""Test script to discover Google ADK package structure."""
import inspect

print("Inspecting Google ADK package...")
print("=" * 60)

try:
    import google.adk
    print("✅ google.adk package found!")
    print(f"   Location: {google.adk.__file__}")
    print()
    
    # List all available attributes
    print("Available exports from google.adk:")
    print("-" * 60)
    
    # Get all public attributes (not starting with _)
    exports = [name for name in dir(google.adk) if not name.startswith('_')]
    
    for export in sorted(exports):
        obj = getattr(google.adk, export)
        obj_type = type(obj).__name__
        
        # Try to get more info
        if inspect.isclass(obj):
            print(f"  📦 {export:20s} (class)")
        elif inspect.ismodule(obj):
            print(f"  📁 {export:20s} (module)")
        elif callable(obj):
            print(f"  ⚙️  {export:20s} (function/callable)")
        else:
            print(f"  📄 {export:20s} ({obj_type})")
    
    print()
    print("=" * 60)
    print("Trying to import common classes...")
    print("-" * 60)
    
    # Try importing common names (case variations)
    import_attempts = [
        "Agent", "agent", "AgentApp", "agent_app",
        "Tool", "tool", "tools", "ToolBase", "tool_base",
        "Step", "step", "steps", "StepBase", "step_base",
        "App", "app", "Application", "application"
    ]
    
    successful_imports = []
    for name in import_attempts:
        if hasattr(google.adk, name):
            try:
                obj = getattr(google.adk, name)
                print(f"✅ {name:20s} -> {type(obj).__name__}")
                successful_imports.append((name, obj))
            except Exception as e:
                print(f"❌ {name:20s} -> Error: {e}")
    
    print()
    print("=" * 60)
    print("Recommended imports:")
    print("-" * 60)
    
    if successful_imports:
        print("You can import:")
        for name, obj in successful_imports:
            print(f"  from google.adk import {name}")
    else:
        print("No standard names found. Check the exports above.")
    
    # Try to inspect submodules
    print()
    print("=" * 60)
    print("Checking for submodules...")
    print("-" * 60)
    
    for name in exports:
        obj = getattr(google.adk, name)
        if inspect.ismodule(obj):
            print(f"📁 Submodule: google.adk.{name}")
            sub_exports = [n for n in dir(obj) if not n.startswith('_')]
            if sub_exports:
                print(f"   Contains: {', '.join(sub_exports[:10])}")
                if len(sub_exports) > 10:
                    print(f"   ... and {len(sub_exports) - 10} more")
    
except ImportError as e:
    print(f"❌ Could not import google.adk: {e}")
    print("   Make sure google-adk is installed: pip install google-adk")
except Exception as e:
    print(f"❌ Error inspecting package: {e}")
    import traceback
    traceback.print_exc()