import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StaticQualityTests(unittest.TestCase):
    def test_test_py_does_not_use_wildcard_imports(self):
        source = (PROJECT_ROOT / "test.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        wildcard_imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and any(alias.name == "*" for alias in node.names)
        ]

        self.assertEqual(wildcard_imports, [])

    def test_pyqt_item_flag_uses_typed_enum_path(self):
        production_source = (PROJECT_ROOT / "test.py").read_text(encoding="utf-8")
        test_source = (
            PROJECT_ROOT / "tests" / "test_curve_selection.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("QtCore.Qt.ItemIsEditable", production_source)
        self.assertNotIn("Qt.ItemIsEditable", test_source)

    def test_pyqt_item_flag_is_not_inverted_to_plain_integer(self):
        production_source = (PROJECT_ROOT / "test.py").read_text(encoding="utf-8")

        self.assertNotIn(
            "~QtCore.Qt.ItemFlag.ItemIsEditable",
            production_source,
        )

    def test_combined_pyqt_flags_have_an_explicit_static_type(self):
        source = (PROJECT_ROOT / "test.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        flag_assignment = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "NAME_ITEM_FLAGS"
                for target in node.targets
            )
        )

        self.assertIsInstance(flag_assignment.value, ast.Call)
        self.assertIsInstance(flag_assignment.value.func, ast.Name)
        self.assertEqual(flag_assignment.value.func.id, "cast")


if __name__ == "__main__":
    unittest.main()
