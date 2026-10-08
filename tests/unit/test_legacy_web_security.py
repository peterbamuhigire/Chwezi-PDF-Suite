"""The localhost web API must not leak the API key or act on client-supplied file paths."""

from io import BytesIO
from pathlib import Path

import pytest

pytest.importorskip("flask")
pytest.importorskip("google.genai")
pytest.importorskip("anthropic")
pytest.importorskip("openai")
pytest.importorskip("reportlab")
pytest.importorskip("PIL")

import web_interface

SECRET = "sk-test-secret-key"


@pytest.fixture
def client(tmp_path: Path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setitem(web_interface.app.config, "UPLOAD_FOLDER", uploads)
    monkeypatch.setattr(web_interface, "_server_state", {}, raising=False)
    web_interface.app.config["TESTING"] = True
    with web_interface.app.test_client() as test_client:
        yield test_client


def configure(client, library: Path) -> None:
    response = client.post(
        "/api/settings",
        json={"ebooks_folder": str(library), "provider": "gemini", "api_key": SECRET},
    )
    assert response.status_code == 200


def upload(client, name: str = "book.pdf") -> dict:
    response = client.post(
        "/api/upload",
        data={"files": (BytesIO(b"%PDF-1.4\n"), name)},
        content_type="multipart/form-data",
    )
    [item] = response.get_json()["files"]
    return item


@pytest.mark.security
def test_settings_never_return_the_api_key(client, tmp_path: Path) -> None:
    configure(client, tmp_path / "library")

    response = client.get("/api/settings")

    assert SECRET not in response.get_data(as_text=True)
    assert response.get_json()["has_api_key"] is True
    cookie = response.headers.get("Set-Cookie", "") + client.get_cookie("session").value
    assert SECRET not in cookie


@pytest.mark.security
def test_blank_key_on_save_keeps_existing_key(client, tmp_path: Path) -> None:
    configure(client, tmp_path / "library")
    client.post("/api/settings", json={"ebooks_folder": str(tmp_path), "api_key": ""})

    assert client.get("/api/settings").get_json()["has_api_key"] is True


@pytest.mark.security
def test_cross_origin_writes_are_rejected(client, tmp_path: Path) -> None:
    response = client.post(
        "/api/settings",
        json={"ebooks_folder": str(tmp_path), "api_key": "attacker"},
        headers={"Origin": "https://evil.example"},
    )

    assert response.status_code == 403
    assert client.get("/api/settings").get_json()["has_api_key"] is False


@pytest.mark.security
def test_same_origin_writes_are_allowed(client, tmp_path: Path) -> None:
    response = client.post(
        "/api/settings",
        json={"ebooks_folder": str(tmp_path), "api_key": SECRET},
        headers={"Origin": "http://localhost"},
    )

    assert response.status_code == 200


@pytest.mark.security
def test_upload_response_exposes_no_server_path(client) -> None:
    item = upload(client)

    assert set(item) == {"id", "filename", "size"}


@pytest.mark.security
def test_organize_ignores_client_supplied_paths(client, tmp_path: Path) -> None:
    library = tmp_path / "library"
    configure(client, library)
    victim = tmp_path / "victim.pdf"
    victim.write_bytes(b"do not move")

    response = client.post(
        "/api/organize",
        json={
            "files": [{"id": "forged", "path": str(victim), "filename": "x.pdf", "category": "A"}]
        },
    )

    assert response.get_json()["organized"] == []
    assert victim.read_bytes() == b"do not move"


@pytest.mark.security
def test_organize_contains_hostile_category(client, tmp_path: Path) -> None:
    library = tmp_path / "library"
    configure(client, library)
    item = upload(client)

    response = client.post(
        "/api/organize",
        json={"files": [{**item, "category": "../../escaped", "rename": "..\\..\\evil"}]},
    )

    assert response.get_json()["organized"] == ["book.pdf"]
    moved = list(library.rglob("*.pdf"))
    assert len(moved) == 1
    assert moved[0].resolve().is_relative_to(library.resolve())
    assert not (tmp_path / "escaped").exists()


@pytest.mark.security
def test_sign_ignores_client_supplied_paths(client, tmp_path: Path) -> None:
    from PIL import Image

    png = BytesIO()
    Image.new("RGBA", (40, 20), (255, 0, 0, 255)).save(png, format="PNG")
    png.seek(0)
    client.post(
        "/api/signature/upload-image",
        data={"signature": (png, "sig.png")},
        content_type="multipart/form-data",
    )
    victim = tmp_path / "victim.pdf"
    victim.write_bytes(b"%PDF-1.4\n")

    response = client.post(
        "/api/signature/process",
        json={"files": [{"filename": "victim.pdf", "path": str(victim)}], "config": {}},
    )

    data = response.get_json()
    assert data["signed"] == []
    assert data["failed"][0]["error"] == "File not found"


@pytest.mark.security
@pytest.mark.parametrize("host", ["127.0.0.1:5000", "localhost:5000", "[::1]:5000"])
def test_loopback_hosts_with_matching_origin_are_allowed(client, tmp_path: Path, host) -> None:
    response = client.post(
        "/api/settings",
        json={"ebooks_folder": str(tmp_path), "api_key": SECRET},
        headers={"Host": host, "Origin": f"http://{host}"},
    )

    assert response.status_code == 200


@pytest.mark.security
def test_dns_rebinding_host_is_rejected(client, tmp_path: Path) -> None:
    response = client.post(
        "/api/settings",
        json={"ebooks_folder": str(tmp_path), "api_key": "attacker"},
        headers={"Host": "evil.example:5000", "Origin": "http://evil.example:5000"},
    )

    assert response.status_code == 403


@pytest.mark.security
def test_organize_tolerates_non_object_items(client, tmp_path: Path) -> None:
    configure(client, tmp_path / "library")

    response = client.post("/api/organize", json={"files": ["not-an-object", 7]})

    assert response.status_code == 200
    assert len(response.get_json()["failed"]) == 2


@pytest.mark.security
def test_content_analysis_defaults_off_and_is_stored(client, tmp_path: Path) -> None:
    assert client.get("/api/settings").get_json()["content_analysis"] is False

    client.post("/api/settings", json={"ebooks_folder": str(tmp_path), "content_analysis": True})

    assert client.get("/api/settings").get_json()["content_analysis"] is True


@pytest.mark.security
def test_idle_sessions_are_evicted_with_their_uploads(client, monkeypatch) -> None:
    item = upload(client)
    [state] = web_interface._server_state.values()
    upload_path = state["uploads"][item["id"]]
    assert upload_path.exists()

    clock = [web_interface.time.monotonic() + web_interface.SESSION_IDLE_SECONDS + 1]
    monkeypatch.setattr(web_interface.time, "monotonic", lambda: clock[0])
    with web_interface.app.test_client() as other:
        other.get("/api/settings")

    assert state not in web_interface._server_state.values()
    assert not upload_path.exists()
