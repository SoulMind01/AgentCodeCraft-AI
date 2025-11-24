"""Quick check of google.adk package structure."""
import google.adk

print("Google ADK Package Inspection")
print("=" * 60)
print(f"Package location: {google.adk.__file__}")
print()

# Show all exports
print("All exports:")
for name in sorted(dir(google.adk)):
    if not name.startswith('_'):
        obj = getattr(google.adk, name)
        print(f"  {name:30s} -> {type(obj).__name__}")

print()
print("=" * 60)
print("Try these imports:")
print()

# Common patterns to try
patterns = [
    ("from google.adk import Agent", "Agent"),
    ("from google.adk import App", "App"),
    ("from google.adk import tools", "tools"),
    ("from google.adk import Tool", "Tool"),
]

for import_stmt, name in patterns:
    if hasattr(google.adk, name):
        print(f"✅ {import_stmt}")
    else:
        print(f"❌ {import_stmt}  (not found)")

print()
print("=" * 60)
print("Package help:")
print("-" * 60)
help(google.adk)

