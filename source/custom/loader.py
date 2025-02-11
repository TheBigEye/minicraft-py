from typing import Optional
from pathlib import Path
import json

class CustomLoader:
    """ Helper class for loading custom game content """

    @staticmethod
    def manifest(mods_dir: Path) -> Optional[dict]:
        """ Load and validate the mods manifest file if present """
        manifest_file = mods_dir / 'manifest.json'

        if not manifest_file.exists():
            return None

        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)

            # Basic manifest validation
            required_fields = ['name', 'version', 'description']
            if not all(field in manifest for field in required_fields):
                print("[CUSTOM] Invalid manifest file, missing required fields!")
                return None

            # Optional sections can be validated here
            optional_sections = {
                'custom_tilemap': dict,
                'custom_player': dict
            }

            for section, expected_type in optional_sections.items():
                if section in manifest and not isinstance(manifest[section], expected_type):
                    print(f"[CUSTOM] Invalid {section} format in manifest.json")
                    manifest.pop(section)

            return manifest

        except json.JSONDecodeError:
            print("[CUSTOM] Invalid manifest.json file format!")
            return None
