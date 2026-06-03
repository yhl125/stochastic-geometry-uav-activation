import unittest
import subprocess
import tempfile
from pathlib import Path


class LeanFormalGuardTests(unittest.TestCase):
    def _formal_readme_row(self, item: str) -> str:
        prefix = f"| `{item}` |"
        for line in Path("formal/README.md").read_text().splitlines():
            if line.startswith(prefix):
                return line
        self.fail(f"missing formal README row for {item}")

    def _lean_check_axiom_pattern(self) -> str:
        script = Path("scripts/lean_check.sh").read_text()
        for line in script.splitlines():
            if line.startswith("axiom_pattern="):
                return line.split("=", 1)[1].strip().strip("'\"")
        self.fail("missing axiom_pattern in scripts/lean_check.sh")

    def _lean_theorem_signature(self, lean_text: str, theorem_name: str) -> str:
        marker = f"theorem {theorem_name}"
        start = lean_text.find(marker)
        self.assertNotEqual(-1, start, f"missing theorem {theorem_name}")
        end = lean_text.find(":= by", start)
        self.assertNotEqual(-1, end, f"missing proof body for theorem {theorem_name}")
        return lean_text[start:end]

    def test_paper_anchor_rows_point_to_specific_formula_symbols(self):
        self.assertIn("No direct Python callsite", self._formal_readme_row(
            "eq6_horizontal_pdf_matches_paper_ref_on_support"
        ))
        self.assertIn("src/formulas.py` `distance_3d_pdf", self._formal_readme_row(
            "eq8_distance_pdf_matches_paper_ref_on_support"
        ))
        self.assertIn("src/formulas.py` `rayleigh_laplace_kernel", self._formal_readme_row(
            "eq15_rayleigh_laplace_identity"
        ))
        self.assertIn("src/formulas.py` `interferer_state_average", self._formal_readme_row(
            "eq16_mixture_matches_paper_ref"
        ))
        self.assertIn("src/formulas.py` `total_power_density", self._formal_readme_row(
            "eq25_total_power_matches_paper_ref"
        ))
        self.assertIn("src/formulas.py` `energy_efficiency_simplified", self._formal_readme_row(
            "eq26_lambda_u_cancels_to_paper_ref"
        ))

    def test_eq7_jacobian_phase2_theorem_is_formalized(self):
        distance = Path("formal/Uav/Distance.lean").read_text()

        self.assertIn("theorem eq7_jacobian", distance)
        self.assertNotIn("Phase 2 target", distance)
        self.assertIn("deriv", distance)

    def test_eq2_los_probability_is_formalized_on_positive_horizontal_distance(self):
        los_probability = Path("formal/Uav/LosProbability.lean").read_text()
        root_module = Path("formal/Uav.lean").read_text()
        theorem_sig = self._lean_theorem_signature(
            los_probability,
            "eq2_los_probability_matches_paper_ref_on_positive_horizontal_distance",
        )

        self.assertIn("import Uav.LosProbability", root_module)
        self.assertIn("def elevationAngleDegrees", los_probability)
        self.assertIn("Real.arctan (H / x) * 180 / Real.pi", los_probability)
        self.assertIn("def losProbabilityFormula", los_probability)
        self.assertIn("def nlosProbabilityFormula", los_probability)
        self.assertIn(
            "theorem eq2_los_probability_matches_paper_ref_on_positive_horizontal_distance",
            los_probability,
        )
        self.assertIn("(hx : 0 < x)", theorem_sig)
        self.assertIn("paperEq2LosProbabilityRhs", theorem_sig)
        self.assertIn("theorem eq2_nlos_probability_is_one_minus_los", los_probability)

    def test_los_probability_module_is_tracked_and_imported_by_root_target(self):
        root_module = Path("formal/Uav.lean").read_text()

        self.assertIn("import Uav.LosProbability", root_module)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "formal/Uav/LosProbability.lean"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            0,
            tracked.returncode,
            "formal/Uav/LosProbability.lean must be tracked because formal/Uav.lean imports it",
        )

    def test_eq6_eq8_pdf_definitions_encode_support_as_piecewise_total_functions(self):
        distance = Path("formal/Uav/Distance.lean").read_text()

        self.assertIn(
            "if 0 ≤ x then paperEq6HorizontalNearestPdfRhs lambda_a x else 0",
            distance,
        )
        self.assertIn(
            "if H ≤ r then paperEq8Distance3dPdfRhs lambda_a H r else 0",
            distance,
        )
        self.assertRegex(
            distance,
            r"theorem eq6_horizontal_pdf_matches_paper_ref_on_support"
            r"[\s\S]*\(hx : 0 ≤ x\)[\s\S]*paperEq6HorizontalNearestPdfRhs",
        )
        self.assertIn("theorem eq6_horizontal_pdf_zero_off_support", distance)
        self.assertRegex(
            distance,
            r"theorem eq6_horizontal_pdf_zero_off_support"
            r"[\s\S]*\(hx : x < 0\)[\s\S]*horizontalNearestPdf lambda_a x = 0",
        )
        self.assertRegex(
            distance,
            r"theorem eq8_distance_pdf_matches_paper_ref_on_support"
            r"[\s\S]*\(hr : H ≤ r\)[\s\S]*paperEq8Distance3dPdfRhs",
        )
        self.assertIn("theorem eq8_distance_pdf_zero_off_support", distance)
        self.assertRegex(
            distance,
            r"theorem eq8_distance_pdf_zero_off_support"
            r"[\s\S]*\(hr : r < H\)[\s\S]*distance3dPdf lambda_a H r = 0",
        )

    def test_eq15_rayleigh_laplace_integral_identity_is_formalized(self):
        rayleigh = Path("formal/Uav/RayleighMixture.lean").read_text()

        self.assertIn("theorem eq15_rayleigh_laplace_identity", rayleigh)
        self.assertIn("∫ x : ℝ in Set.Ioi 0", rayleigh)
        self.assertNotIn("axiom eq15_rayleigh_laplace_identity", rayleigh)

    def test_eq21_ccdf_hamdi_boundary_is_formalized(self):
        rate = Path("formal/Uav/Rate.lean").read_text()
        paper_refs = Path("formal/Uav/PaperRefs.lean").read_text()
        readme = Path("formal/README.md").read_text()

        self.assertIn("def sinrCcdf", rate)
        self.assertIn("def paperEq21HamdiRhs", paper_refs)
        self.assertIn("structure Eq21HamdiChangeOfVariables", rate)
        self.assertIn("sinr_aemeasurable", rate)
        self.assertIn("sinr_nonneg", rate)
        self.assertIn("rate_integrable", rate)
        self.assertIn("rate_nonneg", rate)
        self.assertIn("identity", rate)
        self.assertIn("theorem eq21_rate_tail_integral_identity", rate)
        self.assertIn("theorem eq21_hamdi_identity_from_change_of_variables", rate)
        self.assertIn("Integrable.integral_eq_integral_meas_lt", rate)
        self.assertNotIn("axiom eq21", rate)
        self.assertIn("Eq. 21 layer-cake theorem", readme)

    def test_lean_check_guards_axiom_count(self):
        script = Path("scripts/lean_check.sh").read_text()

        self.assertIn("axiom_count", script)
        self.assertIn("Expected exactly 0 axioms", script)

    def test_lean_check_invokes_explicit_uav_library_target(self):
        script = Path("scripts/lean_check.sh").read_text()

        self.assertIn("lake build Uav", script)
        self.assertNotRegex(script, r"lake build\s*$")
        self.assertNotRegex(script, r"lake build\s*\n")
        self.assertTrue(Path("formal/Uav.lean").exists())
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "formal/Uav.lean"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            0,
            tracked.returncode,
            "formal/Uav.lean must be tracked because scripts/lean_check.sh builds target Uav",
        )

    def test_lean_check_axiom_guard_scans_root_module_too(self):
        script = Path("scripts/lean_check.sh").read_text()

        self.assertIn('rg -n "$axiom_pattern" formal', script)
        self.assertNotIn('rg -n "$axiom_pattern" formal/Uav', script)

    def test_lean_check_axiom_guard_matches_indented_axioms(self):
        pattern = self._lean_check_axiom_pattern()

        with tempfile.TemporaryDirectory() as tmpdir:
            lean_file = Path(tmpdir) / "Bad.lean"
            lean_file.write_text(
                "namespace Bad\n"
                "  axiom bad : False\n"
                "end Bad\n"
            )

            result = subprocess.run(
                ["rg", "-n", pattern, str(lean_file)],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(
            0,
            result.returncode,
            result.stdout + result.stderr,
        )

    def test_lean_check_axiom_guard_matches_prefixed_axioms(self):
        pattern = self._lean_check_axiom_pattern()

        with tempfile.TemporaryDirectory() as tmpdir:
            lean_file = Path(tmpdir) / "Bad.lean"
            lean_file.write_text(
                "namespace Bad\n"
                "@[simp] axiom attrBad : False\n"
                "private axiom privateBad : False\n"
                "@[simp] private axiom attrPrivateBad : False\n"
                "end Bad\n"
            )

            result = subprocess.run(
                ["rg", "-n", pattern, str(lean_file)],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(
            0,
            result.returncode,
            result.stdout + result.stderr,
        )
        self.assertIn("attrBad", result.stdout)
        self.assertIn("privateBad", result.stdout)
        self.assertIn("attrPrivateBad", result.stdout)


if __name__ == "__main__":
    unittest.main()
