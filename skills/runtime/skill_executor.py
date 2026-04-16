def execute_skill(manifest, input_data, context=None):
    return {
        "executed": True,
        "skill_id": manifest.skill_id,
        "input": input_data,
        "context": context or {},
    }
