from window_geometry import centered_geometry


def test_centers_window_on_screen() -> None:
    assert centered_geometry(800, 600, 1920, 1080) == "800x600+560+240"


def test_clamps_oversized_window_to_screen_origin() -> None:
    assert centered_geometry(1200, 900, 1024, 768) == "1200x900+0+0"
