def validate_manifest(manifest) -> bool:
    return bool(getattr(manifest, "skill_id", None) and getattr(manifest, "name", None))
