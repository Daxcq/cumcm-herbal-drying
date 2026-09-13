# -*- coding: utf-8 -*-
"""问题三：全程采用附录3物性的径向温湿耦合求解器。"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "q2_full"))
import solver_q2 as q2


THRESHOLD = 0.15
MAX_TIME = 300000.0
BOUNDARY_DATA_END = 14400.0
C_PLATEAU = float(q2.env_moisture(BOUNDARY_DATA_END))


def run(
    refine=1,
    dt=10.0,
    save_interval=60.0,
    relaxation=0.7,
    tolerance=1.0e-9,
    temperature_extension_offset=0.0,
    moisture_extension_offset=0.0,
):
    nodes, output_indices = q2.build_nodes(refine)
    n = nodes.size
    temperature = np.full(n, q2.T0_C)
    moisture = np.full(n, q2.C0)

    saved_t = [0.0]
    saved_T = [temperature[output_indices].copy()]
    saved_C = [moisture[output_indices].copy()]
    next_save = save_interval
    max_iterations = 0
    crossing = None

    steps = int(np.ceil(MAX_TIME / dt))
    for step in range(1, steps + 1):
        t_old = (step - 1) * dt
        t_new = step * dt
        ta_old = q2.T0_C if step == 1 else float(q2.env_temperature(t_old))
        ta_new = float(q2.env_temperature(t_new))
        if t_old > q2.T_SWITCH:
            ta_old = q2.T_PLATEAU_C
        if t_new > q2.T_SWITCH:
            ta_new = q2.T_PLATEAU_C
        if t_old > BOUNDARY_DATA_END:
            ta_old += temperature_extension_offset
        if t_new > BOUNDARY_DATA_END:
            ta_new += temperature_extension_offset
        ca_old = 0.01963 if step == 1 else float(q2.env_moisture(t_old))
        ca_new = float(q2.env_moisture(t_new))
        if t_old > BOUNDARY_DATA_END:
            ca_old = C_PLATEAU + moisture_extension_offset
        if t_new > BOUNDARY_DATA_END:
            ca_new = C_PLATEAU + moisture_extension_offset

        near_switch = (
            q2.T_SWITCH < t_new <= q2.T_SWITCH + 2.0 * dt
            or BOUNDARY_DATA_END < t_new <= BOUNDARY_DATA_END + 2.0 * dt
        )
        theta = 1.0 if step <= 2 or near_switch else 0.5
        old_max = float(np.max(moisture))
        t_guess = temperature.copy()
        c_guess = moisture.copy()
        for iteration in range(1, 81):
            rho, cp, k, _ = q2.props_appendix3(c_guess, t_guess)
            tri_t = q2.assemble_rate(nodes, k, rho * cp, q2.H_T)
            t_field = q2.implicit_theta(
                temperature, tri_t[:3], tri_t[3], ta_new, ta_old, dt, theta
            )
            _, _, _, diffusivity = q2.props_appendix3(c_guess, t_field)
            tri_c = q2.assemble_rate(nodes, diffusivity, np.ones(n), q2.H_M)
            c_field = q2.implicit_theta(
                moisture, tri_c[:3], tri_c[3], ca_new, ca_old, dt, theta
            )
            c_field = np.maximum(c_field, 0.0)
            error = max(
                np.max(np.abs(t_field - t_guess)) / (1.0 + np.max(np.abs(t_field))),
                np.max(np.abs(c_field - c_guess)) / (1.0 + np.max(np.abs(c_field))),
            )
            t_guess = relaxation * t_field + (1.0 - relaxation) * t_guess
            c_guess = relaxation * c_field + (1.0 - relaxation) * c_guess
            if error < tolerance:
                break
        else:
            raise RuntimeError(f"t={t_new}: Picard迭代未收敛")

        max_iterations = max(max_iterations, iteration)
        temperature = t_guess
        moisture = c_guess
        new_max = float(np.max(moisture))
        if crossing is None and old_max >= THRESHOLD and new_max < THRESHOLD:
            fraction = (old_max - THRESHOLD) / (old_max - new_max)
            crossing = t_old + fraction * dt

        if t_new + 1e-9 >= next_save:
            saved_t.append(t_new)
            saved_T.append(temperature[output_indices].copy())
            saved_C.append(moisture[output_indices].copy())
            next_save += save_interval

        if crossing is not None and t_new >= np.ceil(crossing / save_interval) * save_interval:
            break

    if crossing is None:
        raise RuntimeError(f"{MAX_TIME} s 内未达到阈值")
    return (
        np.asarray(saved_t), np.asarray(saved_T), np.asarray(saved_C),
        float(crossing), max_iterations,
    )


if __name__ == "__main__":
    refine = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    dt = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    output = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "outputs/q3/q3_fullA3.npz"
    output.parent.mkdir(parents=True, exist_ok=True)
    times, temperature, moisture, crossing, max_iterations = run(refine=refine, dt=dt)
    np.savez(output, t=times, T=temperature, C=moisture,
             crossing=crossing, max_iterations=max_iterations)
    print("crossing_s", crossing)
    print("crossing_h", crossing / 3600.0)
    print("max_iterations", max_iterations)
    print("last_saved_s", times[-1])
    print("finite", np.isfinite(temperature).all() and np.isfinite(moisture).all())
    print("nonnegative", moisture.min() >= -1e-10)
    for hour in range(6, int(np.floor(crossing / 21600.0)) * 6 + 1, 6):
        idx = int(hour * 3600 / 60)
        print(hour, moisture[idx, [0, 5, 10, 15, 20]])
