# DBT Dependency Viewer

DBT Lineage Viewer is a command-line tool for visualizing the upstream and
downstream dependencies of a specified DBT model within a DBT project. It
generates an HTML file containing a diagram of the dependency tree.

## Installation

Install the package using pip:

```bash
pip install dbt-lineage-viewer
```

## Usage
To use the DBT Dependency Viewer, please navigate into your dbt project folder
and run the following command:

```bash
dbt-lineage-viewer <model_name> --max-depth <max_depth> --output <output_file>
```
Replace `<model_name>` with the name of the DBT model you want to analyze,
`<max_depth>` with the maximum depth for the dependency tree, and
`<output_file>` with the name of the output HTML file.

## Parameters
model_name: The name of the DBT model to analyze (required).
max_depth: The maximum depth for the dependency tree (optional, default: 3).
output: The name of the output HTML file (optional, default: "test.html").

## Example
Analyze the tbl_acquisition_funnel model with a maximum depth of 3, and
generate an output HTML file named dependency_tree.html:

```bash
dbt-lineage-viewer tbl_acquisition_funnel --max-depth 3 --output dependency_tree.html
```
