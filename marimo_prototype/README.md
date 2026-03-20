# gprMax Marimo Prototype

> A reactive, web-based interface for configuring, running, and visualising gprMax simulations — built with [marimo](https://github.com/marimo-team/marimo).

---

## Overview

This prototype integrates **marimo** into [gprMax](https://github.com/gprMax/gprMax) to replace static `.in` file editing with a live, reactive GUI. All simulation parameters (domain, material, waveform, source, receiver) are exposed as interactive controls in the browser. Changing any value immediately propagates through the notebook — no manual re-running of cells required.

Two workflows are supported:

| Workflow | File | Simulation method |
|---|---|---|
| **A-scan** | `reactascan.py` | Python API (`gprMax.gprMax.main()`) |
| **B-scan** | `reactbscan.py` | CLI via `subprocess`, then `outputfiles_merge` |

---

## Running the Apps

**A-scan** — single trace:
```bash
marimo run reactascan.py
```
Adjust the parameters in the sidebar, then click **Run Simulation** to see the trace.

**B-scan** — radargram (make sure `bscan.in` is in the same folder):
```bash
marimo run reactbscan.py
```
Set the B-scan start, end, and step positions in the sidebar. The app runs all traces automatically and displays the radargram.

> **NOTE: THE B-SCAN CURRENTLY RUNS GPRMAX VIA THE CLI. IT WILL BE TRANSFORMED TO USE THE PYTHON API DIRECTLY TO RUN SIMULATIONS, IN LINE WITH THE A-SCAN APPROACH.**

**To edit the code while using the UI:**
```bash
marimo edit reactascan.py
marimo edit reactbscan.py
```

---

## File Structure

```
marimo_prototype/
├── reactascan.py           # Marimo app: single-trace (A-scan) workflow
├── reactbscan.py           # Marimo app: multi-trace (B-scan) workflow
├── react_model_builder.py  # GPRMaxModel class — builds .in file content
├── react_run_simulation.py # Runs gprMax via Python API, returns logs
└── bscan.in                # Template .in file used by the B-scan runner
```

---

## Module Descriptions

### `react_model_builder.py` — `GPRMaxModel`

A plain Python class that holds all model parameters and serialises them into gprMax `.in` file commands via `to_in_file()`.

**Default configuration:**

| Parameter | Default |
|---|---|
| Spatial resolution (dx/dy/dz) | 0.02 m |
| Domain | 0.4 × 0.4 × 0.2 m |
| Time window | 5 ns |
| PML cells | 0 |
| Material (ε, σ, μr, σm) | 4, 0.01, 1, 0 — `half_space` |
| Waveform | Gaussian, 1 V/m, 100 MHz — `pulse` |
| Source (Hertzian dipole, z-dir) | (0.1, 0.1, 0.05) m |
| Receiver | (0.15, 0.1, 0.05) m |

**Usage:**
```python
from react_model_builder import GPRMaxModel

model = GPRMaxModel()
model.dx = 0.01
model.material["eps"] = 6
print(model.to_in_file())
```

---

### `react_run_simulation.py` — `run_model()`

Writes the model to a temporary file (`temp_model.in`), invokes `gprMax.gprMax.main()` via the Python API, captures all stdout into a string buffer, and returns the output filename and captured logs.

```python
from react_run_simulation import run_model

output_file, logs = run_model(model)
```

> **Note:** gprMax is invoked by patching `sys.argv` and redirecting stdout with `contextlib.redirect_stdout`. This keeps the simulation in-process, avoiding subprocess overhead.

---

### `bscan.in` — B-scan template

A minimal gprMax input file used as the **base template** for B-scan runs. The B-scan runner reads this file line-by-line and rewrites any parameter line that matches a UI-controlled field before saving to `temp_bscan.in`.

Default scene: 0.1 × 0.1 × 0.1 m domain, soil half-space (ε=4), Ricker wavelet at 500 MHz, z-directed dipole, a receiver offset 0.01 m in x, and a 3 cm soil box at the base.

---

### `reactascan.py` — A-scan Marimo App

A single-page marimo app for running one gprMax trace and visualising it.

**Sidebar controls (collapsible accordions):**

- **Domain** — dx, dy, dz, domain_x, domain_y, domain_z
- **Material** — εr, σ, μr, σm, material name (dropdown)
- **Waveform** — amplitude, frequency, waveform name
- **Source** — dipole direction (x/y/z dropdown), x, y, z
- **Receiver** — x, y, z
- **Run Simulation** button

**App flow:**

1. UI values are applied to a `GPRMaxModel` instance.
2. `run_model()` is called — gprMax runs in-process and logs are captured.
3. ANSI escape codes are stripped; logs are displayed in a styled dark terminal panel.
4. `tools.plot_Ascan.mpl_plot` renders the time-domain trace.

**Run:**
```bash
marimo run reactascan.py      # app mode (no code visible)
marimo edit reactascan.py     # notebook / edit mode
```

---

### `reactbscan.py` — B-scan Marimo App

A marimo app for running a multi-trace B-scan survey and rendering the radargram.

**Additional sidebar section — B-scan Parameters:**

- Start position (m)
- End position (m)
- Step size (m)

The number of traces is computed as:
```
n = int((end - start) / step) + 1
```

**App flow:**

1. `bscan.in` is read and every recognised command line is overwritten with the current UI values, producing `temp_bscan.in`.
2. gprMax is called via `subprocess`:
   ```
   python -m gprMax temp_bscan.in -n <n>
   ```
3. Per-trace `.out` files are merged with `tools.outputfiles_merge.merge_files()`, producing `temp_bscan_merged.out`.
4. The merged HDF5 file is opened with `h5py`; the chosen field component (Ex/Ey/Ez/Hx/Hy/Hz) is read across all receivers.
5. `tools.plot_Bscan.mpl_plot` renders the radargram.

> **Prototype note (from source):** The B-scan runner currently uses `subprocess` for stability. A future version will switch to the direct Python API approach used in `reactascan.py`.

**Run:**
```bash
marimo run reactbscan.py
marimo edit reactbscan.py
```

---
