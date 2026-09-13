from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for directory in ("q1_preheat", "q2_full", "q3_drying", "q4_shrinkage"):
    sys.path.insert(0, str(ROOT / "src" / directory))

import solver_q1 as q1
import solver_q2 as q2
import solver_q4 as q4


class ModelSmokeTests(unittest.TestCase):
    def test_thermal_diffusivity(self):
        self.assertAlmostEqual(q1.ALPHA, 1.6886e-7, delta=5e-12)

    def test_kelvin_conversion_in_properties(self):
        _, _, _, d_c = q2.props_appendix3(np.array([1.0]), np.array([50.0]))
        expected = 2.4e-3 * np.exp(-0.45) * np.exp(-3850.0 / 323.15)
        self.assertAlmostEqual(float(d_c[0]), float(expected), places=15)

    def test_temperature_plateau(self):
        values = q4.ambient_temperature(np.array([7200.0, 8000.0, 14400.0]))
        self.assertAlmostEqual(float(values[1]), q2.T_PLATEAU_C, places=12)
        self.assertAlmostEqual(float(values[2]), q2.T_PLATEAU_C, places=12)

    def test_radius_curve(self):
        _, radii, radius, _ = q4.read_radius_curve()
        self.assertTrue(np.all(np.diff(radii) <= 1e-12))
        self.assertAlmostEqual(float(radius(0.0)), 0.02, places=12)


if __name__ == "__main__":
    unittest.main()
