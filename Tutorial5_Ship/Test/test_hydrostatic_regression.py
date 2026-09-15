"""GUI 환경에서 실행: python -m unittest Test.test_hydrostatic_regression"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication, QWidget, QComboBox

from Model.HydrostaticValue import Calculate
from ViewModel.Play import Playing
from ViewModel.BodyPlan import BodyPlan
from ViewModel.HydrostaticCurveView import HydrostaticCurveView


class HydrostaticRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.data = Playing.run()

    def test_box_bottom_and_shell_volume(self):
        offset = {
            "stations": [0, 1, 2], "waterlines": list(range(11)),
            "half_breadth": {s: [10.0] * 11 for s in range(3)},
        }
        dimension = {
            "LBP": 100, "B": 20, "KG": 0,
            "Density of sea water": 1.025, "Mean plate thickness": 0.02,
        }
        calc = Calculate(offset, dimension, {"Step": 1}, 10)
        # 양쪽 측면 2,000 + 선저 2,000 (끝단은 제외한 현재 근사 정의).
        self.assertAlmostEqual(calc.WSA(), 4000)
        self.assertAlmostEqual(calc.Volume_ext(), 20080)
        self.assertAlmostEqual(calc.Displacement_ext(), 20080 * 1.025)

    def test_real_ship_values_and_draft_range(self):
        rows = {r["draft"]: r for r in self.data["results"]}
        self.assertEqual(min(rows), 1)
        self.assertEqual(max(rows), 29)
        self.assertEqual(len(rows), 60)
        row = rows[20.8]
        self.assertAlmostEqual(row["wsa"], 28216.27439000691)
        self.assertAlmostEqual(row["volume"], 333126.45652)
        self.assertAlmostEqual(row["lcb"], 10.378562564889624)
        self.assertAlmostEqual(row["mtc"], 4007.9292332662235)
        for r in rows.values():
            self.assertAlmostEqual(r["displacement"], r["volume"] * 1.025)
            self.assertAlmostEqual(r["cp"], r["cb"] / r["cm"])
            self.assertAlmostEqual(r["tpc"], r["waterplane_area"] * 1.025 / 100)
            self.assertAlmostEqual(r["km_t"], r["kb"] + r["bm_t"])

    def test_overhang_does_not_move_ap_or_enter_calculations(self):
        self.assertEqual(self.data["offset_data"]["stations"], list(range(21)))
        self.assertIn(-0.333, self.data["body_data"]["stations"])
        self.assertIn(-0.166, self.data["body_data"]["stations"])
        host, combo = QWidget(), QComboBox()
        view = BodyPlan(host, combo)
        view.update_body(self.data["body_data"], self.data["dimension"])
        self.assertEqual(view.profile_axes.get_xlim(), (159, 318))
        section = view.section_axes.lines[0]
        self.assertEqual(list(section.get_xdata())[:2], [0, 27.4])
        self.assertEqual(list(section.get_ydata())[:2], [0, 0])
        combo.setCurrentText("Aft Body")
        self.assertAlmostEqual(view.profile_axes.get_xlim()[0], -0.333 * 318 / 20)
        self.assertEqual(view.profile_axes.get_xlim()[1], 159)
        view.canvas.draw()
        host.close()

    def test_curve_scale_is_fixed_and_volume_displacement_separate(self):
        host = QWidget()
        view = HydrostaticCurveView(host)
        rows = self.data["results"]
        view.update_curve(rows)
        full_x = list(view.axes.lines[0].get_xdata())
        self.assertNotEqual(full_x, list(view.axes.lines[1].get_xdata()))
        view.update_curve(rows[-3:])
        self.assertEqual(list(view.axes.lines[0].get_xdata()), full_x[-3:])
        view.canvas.draw()
        view.update_curve([])
        self.assertEqual(len(view.axes.lines), 0)
        host.close()


if __name__ == "__main__":
    unittest.main()
