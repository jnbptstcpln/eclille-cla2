
def capitalize_name(name: str):
    return "-".join(
        " ".join(
            c2.capitalize() for c2 in c1.split(" ")
        )
        for c1 in name.split("-")
    )
