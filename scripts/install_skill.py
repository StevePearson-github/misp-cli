#!/usr/bin/env python3
"""
MISP CLI Skill Installer

This script installs the MISP CLI skill to ~/.kilocode/skills/misp-cli/
and optionally creates a distributable .skill package.

Usage:
    python install_skill.py [--package] [--output-dir <dir>]

Options:
    --package       Create a distributable .skill package
    --output-dir    Output directory for the .skill package (default: ./dist)
    --help          Show this help message
"""

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path


def get_script_dir() -> Path:
    """Get the directory containing this script."""
    return Path(__file__).parent.resolve()


def get_project_root() -> Path:
    """Get the project root directory (parent of scripts/)."""
    script_dir = get_script_dir()
    # If script is in scripts/ directory, go up one level
    if script_dir.name == 'scripts':
        return script_dir.parent
    return script_dir


def install_skill(source_dir: Path, dest_dir: Path) -> bool:
    """Install the skill to the destination directory."""
    print("=" * 40)
    print("MISP CLI Skill Installer")
    print("=" * 40)
    print()
    print(f"📂 Source directory: {source_dir}")
    print(f"📂 Target directory: {dest_dir}")
    print()

    # Check if source exists
    if not source_dir.exists():
        print(f"❌ Error: Source directory does not exist: {source_dir}")
        return False

    if not source_dir.is_dir():
        print(f"❌ Error: Source path is not a directory: {source_dir}")
        return False

    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Copy skill files (SKILL.md, README.md)
    print("Copying skill files...")

    for item in source_dir.iterdir():
        if item.name in ['.git', '__pycache__', '.DS_Store', '.gitignore']:
            continue
        if item.is_file() and item.suffix in ['.pyc', '.swp', '.swo']:
            continue

        dest_path = dest_dir / item.name
        if item.is_dir():
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(item, dest_path)
            print(f"  Copied: {item.name}/")
        else:
            shutil.copy2(item, dest_path)
            print(f"  Copied: {item.name}")

    # Also copy the src/misp_cli folder to scripts/src/misp_cli
    project_root = get_project_root()
    misp_cli_source_dir = project_root / 'src' / 'misp_cli'
    scripts_dest_dir = dest_dir / 'scripts'
    scripts_src_dest_dir = scripts_dest_dir / 'src' / 'misp_cli'

    if misp_cli_source_dir.exists() and misp_cli_source_dir.is_dir():
        print()
        print("Copying src/misp_cli to scripts/src...")
        scripts_src_dest_dir.mkdir(parents=True, exist_ok=True)

        for item in misp_cli_source_dir.iterdir():
            if item.name in ['.git', '__pycache__', '.DS_Store', '.gitignore']:
                continue
            if item.is_file() and item.suffix in ['.pyc', '.swp', '.swo']:
                continue

            dest_path = scripts_src_dest_dir / item.name
            if item.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(item, dest_path)
                print(f"  Copied: scripts/src/misp_cli/{item.name}/")
            else:
                shutil.copy2(item, dest_path)
                print(f"  Copied: scripts/src/misp_cli/{item.name}")

    # Copy pyproject.toml and README.md to scripts for uv resolution
    pyproject_source = project_root / 'pyproject.toml'
    pyproject_dest = scripts_dest_dir / 'pyproject.toml'
    if pyproject_source.exists():
        shutil.copy2(pyproject_source, pyproject_dest)
        print(f"  Copied: scripts/pyproject.toml")

    readme_source = project_root / 'README.md'
    readme_dest = scripts_dest_dir / 'README.md'
    if readme_source.exists():
        shutil.copy2(readme_source, readme_dest)
        print(f"  Copied: scripts/README.md")

    print()
    print(f"✅ Skill installed successfully to: {dest_dir}")
    return True


def create_package(source_dir: Path, output_dir: Path) -> bool:
    """Create a distributable .skill package."""
    skill_name = source_dir.name
    package_file = output_dir / f"{skill_name}.skill"

    print()
    print("📦 Creating .skill package...")
    print(f"   Output: {package_file}")
    print()

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(package_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    # Skip unwanted files
                    if any(skip in file_path.name for skip in ['.git', '__pycache__', '.DS_Store', '.gitignore']):
                        continue
                    if file_path.suffix in ['.pyc', '.swp', '.swo']:
                        continue

                    # Use just the filename at the root of the zip
                    arcname = file_path.name
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print()
        print(f"✅ Package created successfully: {package_file}")
        return True

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="MISP CLI Skill Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install the skill to ~/.kilocode/skills/misp-cli/
  python install_skill.py

  # Install and create a .skill package in ./
  python install_skill.py --package

  # Install and create a .skill package in a custom directory
  python install_skill.py --package --output-dir /tmp/packages
        """
    )

    parser.add_argument(
        '--package',
        action='store_true',
        help='Create a distributable .skill package'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('./dist'),
        help='Output directory for the .skill package (default: ./dist)'
    )

    args = parser.parse_args()

    # Determine directories
    project_root = get_project_root()
    skill_source_dir = project_root / 'skill'
    skill_dest_dir = Path.home() / '.kilocode' / 'skills' / 'misp-cli'

    # Install the skill
    if not install_skill(skill_source_dir, skill_dest_dir):
        sys.exit(1)

    # Create package if requested
    if args.package:
        if not create_package(skill_source_dir, args.output_dir):
            sys.exit(1)

    print()
    print("=" * 40)
    print("Installation Complete!")
    print("=" * 40)
    print()
    print("The MISP CLI skill is now available.")
    print(f"You can verify the installation at: {skill_dest_dir}")
    print()
    print("To use the skill, restart Claude or refresh your session.")


if __name__ == '__main__':
    main()
