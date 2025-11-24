import os
from pathlib import Path

# ĐƯỜNG DẪN THƯ MỤC GỐC CỦA BẠN
ROOT = Path(r"C:\Users\Foxy\Downloads\File 5h_4_11\MetaUpdate")


def build_tree(path: Path):
    """Đệ quy quét thư mục và trả về cấu trúc dạng list (tree)."""
    entries = sorted(
        path.iterdir(),
        key=lambda p: (p.is_file(), p.name.lower())
    )
    tree = []
    for e in entries:
        if e.is_dir():
            tree.append({
                "name": e.name,
                "type": "dir",
                "children": build_tree(e)
            })
        else:
            tree.append({
                "name": e.name,
                "type": "file"
            })
    return tree


def tree_to_html(tree):
    """Chuyển cây thư mục thành HTML <ul><li> lồng nhau."""
    html = "<ul>\n"
    for node in tree:
        if node["type"] == "dir":
            html += f'<li class="dir"><span>{node["name"]}/</span>\n'
            html += tree_to_html(node["children"])
            html += "</li>\n"
        else:
            html += f'<li class="file"><span>{node["name"]}</span></li>\n'
    html += "</ul>\n"
    return html


def main():
    if not ROOT.exists():
        print(f"Thư mục không tồn tại: {ROOT}")
        return

    tree = build_tree(ROOT)
    body_html = tree_to_html(tree)

    template = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Cấu trúc dự án - {ROOT.name}</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 20px;
      background: #0f172a;
      color: #e5e7eb;
    }}
    h1 {{
      font-size: 20px;
      margin-bottom: 16px;
    }}
    .root-path {{
      font-size: 12px;
      color: #9ca3af;
      margin-bottom: 20px;
    }}
    ul {{
      list-style-type: none;
      padding-left: 20px;
      margin: 4px 0;
      border-left: 1px solid #1f2937;
    }}
    li {{
      margin: 2px 0;
      position: relative;
      padding-left: 6px;
    }}
    li::before {{
      content: "";
      position: absolute;
      left: -1px;
      top: 10px;
      width: 8px;
      height: 1px;
      background: #1f2937;
    }}
    .dir > span {{
      font-weight: 600;
      color: #facc15;
    }}
    .file > span {{
      color: #e5e7eb;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <h1>Cấu trúc dự án: {ROOT.name}</h1>
  <div class="root-path">{ROOT}</div>
  {body_html}
</body>
</html>
"""

    out_file = ROOT / "project_structure.html"
    out_file.write_text(template, encoding="utf-8")
    print(f"Đã tạo file: {out_file}")
    print("Mở file này bằng trình duyệt để xem cây cấu trúc dự án.")


if __name__ == "__main__":
    main()
