from pathlib import Path
import subprocess
import tempfile
from IPython.display import Image, SVG, display


def save_and_render_langgraph_mermaid(
    workflow,
    name: str,
    assets_dir_name: str = "assets",
):
    """
    Render a LangGraph workflow graph and display inline.

    - Output is ALWAYS saved under: project-root/<assets_dir_name>/
    - Works regardless of current working directory or notebook location
    - Does NOT persist the .mmd file

    Args:
        workflow: Compiled LangGraph workflow
        name: Output filename (must end with .png or .svg)
        assets_dir_name: Folder under project root to store images
    """

    if not name.endswith((".png", ".svg")):
        raise ValueError("name must end with .png or .svg")

    fmt = name.rsplit(".", 1)[-1]

    # 🔹 Derive project root from utils/mermaid.py location
    project_root = Path(__file__).resolve().parents[1]
    assets_dir = project_root / assets_dir_name
    assets_dir.mkdir(parents=True, exist_ok=True)

    img_path = assets_dir / name

    mermaid = workflow.get_graph().draw_mermaid()

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".mmd",
        delete=True,
    ) as tmp:
        tmp.write(mermaid)
        tmp.flush()

        subprocess.run(
            ["mmdc", "-i", tmp.name, "-o", str(img_path)],
            check=True,
        )

    # 🔹 Display inline
    if fmt == "svg":
        display(SVG(filename=str(img_path)))
    else:
        display(Image(filename=str(img_path)))