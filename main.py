"""
This script generates a mermaid chart of the dependency tree of a dbt model.

It purely uses the model files in the project directory and does not rely on
the dbt manifest.json file, which means it does not need to run `dbt compile`
first.
"""
from model import find_dbt_project_root
from model import generate_downstream_tree
from model import generate_upstream_tree
from model import get_all_models

from mermaid import export_diagram_to_html
from mermaid import generate_mermaid_code

import click


@click.command()
@click.argument("model_name")
@click.option("--max-depth", default=3, help="Maximum depth of dependencies.")
@click.option("--output", default="test.html", help="Output HTML file path.")
@click.option("--model-dir-name", default="models", help="Model folder name")
@click.option("--data-dir-name", default="data", help="Data folder name")
@click.option("--snapshot-dir-name", default="snapshots", help="Snapshots folder name")
def main(
    model_name: str,
    max_depth: int,
    output: str,
    model_dir_name: str,
    data_dir_name: str,
    snapshot_dir_name

):
    try:
        project_root = find_dbt_project_root()
    except FileNotFoundError as error:
        print(error)
        exit(1)

    # Time consuming
    all_models = get_all_models(
        project_root, model_dir_name, data_dir_name, snapshot_dir_name
    )

    # Traverse downstream models (slower with bigget max_depth)
    downstream_models = generate_downstream_tree(
        model_name, all_models, max_depth=max_depth
    )
    downstream_tree = { model_name: downstream_models }

    # Traverse upstream models (fast, max_depth has little effect)
    upstream_models = generate_upstream_tree(
        model_name, all_models, max_depth=max_depth
    )
    upstream_tree = { model_name: upstream_models }

    # Convert dependency tree to mermaid code
    downstream_chart = generate_mermaid_code(downstream_tree, downstream=True)
    upstream_chart = generate_mermaid_code(upstream_tree, downstream=False)

    mermaid_code = f"""
        flowchart LR
        {downstream_chart}
        {upstream_chart}
    """

    # Wrap mermaid code with html and output it so can be displayed
    # in local browser
    export_diagram_to_html(output, mermaid_code)
    print(f"You can now open {output} with your browser to view dependencies")
