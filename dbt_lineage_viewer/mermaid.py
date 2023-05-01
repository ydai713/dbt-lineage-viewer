from typing import Dict


def generate_mermaid_code(
    d: Dict[str, Dict], 
    parent=None,
    mentioned_nodes=set(),
    visited_edges=set(),
    downstream: bool = False
) -> str:
    code = ""
    
    if parent is None:
        mentioned_nodes = set()
        visited_edges = set()
    
    for key, value in d.items():
        if parent:
            edge = (parent, key)
            if key not in mentioned_nodes:
                mentioned_nodes.add(key)
            if edge not in visited_edges:
                visited_edges.add(edge)
                # this is a bug from mermaid (click is a mermaid keyword)
                key = key.replace("click", "Click")
                parent = parent.replace("click", "Click")

                code += (
                    f"{key} --> {parent}\n" if not downstream 
                    else f"{parent} --> {key}\n"
                )
        if value:
            code += generate_mermaid_code(
                value, 
                key,
                mentioned_nodes,
                visited_edges, 
                downstream=downstream
            )
    
    return code


def export_diagram_to_html(output: str, mermaid_code: str):
    html = (
        f"""
        <!DOCTYPE html>
        <html lang="en">
          <body>
            <pre class="mermaid">
            {mermaid_code}
            </pre>
            <script type="module">
              import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            </script>
          </body>
        </html>
        """
    )
    with open(output, "w") as fout:
        fout.write(html)
