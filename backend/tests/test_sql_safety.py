import ast
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "app" / "db"


def test_no_fstring_or_interpolated_sql():
    """Verify that no SQL queries are constructed using f-strings or string formatting."""
    sql_keywords = ["select", "insert", "update", "delete", "create", "alter", "drop"]

    for py_file in DB_DIR.glob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(py_file))

        for node in ast.walk(tree):
            # Check for JoinedStr (f-strings)
            if isinstance(node, ast.JoinedStr):
                # Check if this f-string contains SQL keywords
                raw_text = "".join(
                    part.value for part in node.values if isinstance(part, ast.Constant)
                ).lower()
                for kw in sql_keywords:
                    assert kw not in raw_text, (
                        f"Found forbidden f-string SQL query containing '{kw}' in {py_file.name}:line {node.lineno}"
                    )

            # Check for .format() calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "format" and isinstance(node.func.value, ast.Constant):
                    s_val = str(node.func.value.value).lower()
                    for kw in sql_keywords:
                        assert kw not in s_val, (
                            f"Found forbidden .format() SQL query containing '{kw}' in {py_file.name}:line {node.lineno}"
                        )

