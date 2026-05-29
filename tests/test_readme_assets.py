import re
from pathlib import Path


def test_readme_embedded_images_live_in_docs_images():
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    img_sources = re.findall(r"<img\s+[^>]*src=\"([^\"]+)\"", content)
    assert img_sources, "No embedded <img> tags found in README.md"

    for src in img_sources:
        assert src.startswith("docs/images/"), f"README image should live in docs/images: {src}"
        image_path = readme_path.parent / src
        assert image_path.exists(), f"Missing README image file: {src}"
