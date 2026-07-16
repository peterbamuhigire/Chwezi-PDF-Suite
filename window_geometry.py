"""Window-placement helpers shared by desktop launchers."""


def centered_geometry(
    width: int,
    height: int,
    screen_width: int,
    screen_height: int,
) -> str:
    """Return Tk geometry centered on the available screen dimensions."""
    x = max(0, (screen_width - width) // 2)
    y = max(0, (screen_height - height) // 2)
    return f"{width}x{height}+{x}+{y}"
