

def capitalize_name(name: str):
    return "-".join(c.capitalize() for c in name.split("-"))
