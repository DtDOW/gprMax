"""
Prototype Note:

This implementation was my first method and currently runs gprMax using the CLI via subprocess.
This approach ensures stability and compatibility with the existing workflow.

Future Work:
This will be upgraded to directly interface with gprMax similar to "reactascan.py",
enabling reactive simulations and tighter integration with marimo.
"""

import marimo as mo
import numpy as np
import matplotlib.pyplot as plt

app = mo.App()

@app.cell 
def _():
    import numpy as np 
    import marimo as mo
    import subprocess
    return np, mo, subprocess


# UI 

@app.cell
def _(mo):
    # Here we are creating the title symbol (gprMax)
    title = mo.md("""
<div style="font-size:40px;font-weight:800;text-align:center;margin:0;padding:0;">
<span style="color:#2563eb">gpr</span><span style="color:#1f2937">MAX</span>
</div>
<hr style="border-color:#d1d5db;margin:6px 0 12px 0;">
""")

    # We are defining numbers to enter here with a given value. 
    # I am not specifically using slider as getting an exact value in slider is a bit rigerous
    # where as entering a value is more easy with no uper limit
    # but they can be changed to slider by replacing "mo.ui.number()" with "mo.ui.slider()"
    # Bscan Parameters
    start = mo.ui.number(value=0, step=0.01, label="Start Position (m)")
    end = mo.ui.number(value=0.06, step=0.01, label="End Position (m)")
    step = mo.ui.number(value=0.02, step=0.01, label="Step Size (m)")

    bscan_section = mo.accordion({
        "B-scan Parameters": mo.vstack([start, end, step])
    })

    # Domain 
    dx = mo.ui.number(value=0.01, step=0.001, label="dx (m)")
    dy = mo.ui.number(value=0.01, step=0.001, label="dy (m)")
    dz = mo.ui.number(value=0.01, step=0.001, label="dz (m)")

    domain_x = mo.ui.number(value=0.1, step=0.05, label="domain_x (m)")
    domain_y = mo.ui.number(value=0.1, step=0.05, label="domain_y (m)")
    domain_z = mo.ui.number(value=0.1, step=0.05, label="domain_z (m)")

    domain_section = mo.accordion({
        "Domain": mo.vstack([dx, dy, dz, domain_x, domain_y, domain_z])
    })

    # Material
    eps = mo.ui.number(value=4, step=0.1, label="Permittivity (εr)")
    sigma = mo.ui.number(value=0.0, step=0.01, label="Conductivity (σ)")
    mur = mo.ui.number(value=1, step=0.1, label="Magnetic permeability (μr)")
    sigma_m = mo.ui.number(value=0, step=0.01, label="Magnetic conductivity (σm)")

    material_name = mo.ui.dropdown(
        options=["half_space","soil","concrete","custom_material"],
        value="soil",
        label="Material name"
    )

    material_section = mo.accordion({
        "Material": mo.vstack([eps, sigma, mur, sigma_m, material_name])
    })

    # Waveform
    amplitude = mo.ui.number(value=1, step=0.1, label="Amplitude")
    frequency = mo.ui.number(value=1e8, step=1e8, label="Frequency (Hz)")
    waveform_name = mo.ui.text(value="pulse", label="Waveform name")

    waveform_section = mo.accordion({
        "Waveform": mo.vstack([amplitude, frequency, waveform_name])
    })

    # source 
    direction = mo.ui.dropdown(options=["x","y","z"], value="z", label="Dipole direction")

    src_x = mo.ui.number(value=0.05, step=0.01, label="Source x (m)")
    src_y = mo.ui.number(value=0.05, step=0.01, label="Source y (m)")
    src_z = mo.ui.number(value=0.05, step=0.01, label="Source z (m)")

    source_section = mo.accordion({
        "Source": mo.vstack([direction, src_x, src_y, src_z])
    })

    # Reciever
    rx_x = mo.ui.number(value=0.06, step=0.01, label="Receiver x (m)")
    rx_y = mo.ui.number(value=0.05, step=0.01, label="Receiver y (m)")
    rx_z = mo.ui.number(value=0.05, step=0.01, label="Receiver z (m)")

    field_component = mo.ui.dropdown(
        options=["Ex","Ey","Ez","Hx","Hy","Hz"],
        value="Ez",
        label="Field component"
    )

    receiver_section = mo.accordion({
        "Receiver": mo.vstack([rx_x, rx_y, rx_z])
    })

    sidebar = mo.vstack([
        title,
        bscan_section,
        domain_section,
        material_section,
        waveform_section,
        source_section,
        receiver_section,
        field_component
    ])

    return (
        start,end,step,
        dx,dy,dz,domain_x,domain_y,domain_z,
        eps,sigma,mur,sigma_m,material_name,
        amplitude,frequency,waveform_name,
        direction,src_x,src_y,src_z,
        rx_x,rx_y,rx_z,
        field_component,
        sidebar
    )

# Creating sidebar 

@app.cell
def _(mo, sidebar):
    mo.sidebar(sidebar)

# Run gprMax
# Right now we are following CLI based run for Bscan, but in future model I will be transforming it. 
# Similar to Ascan by directly calling python API to run Bscan with a predefined model

@app.cell
def _(start,end,step,
        dx,dy,dz,domain_x,domain_y,domain_z,
        eps,sigma,mur,sigma_m,material_name,
        amplitude,frequency,waveform_name,
        direction,src_x,src_y,src_z,
        rx_x,rx_y,rx_z,subprocess):

    # number of bscan
    n = int((end.value - start.value) / step.value) + 1

    base_input = "bscan.in"

    
    with open(base_input) as f:
        lines = f.readlines()

    new_lines = []

    for line in lines:
        
        if line.startswith("#dx_dy_dz"):
            new_lines.append(f"#dx_dy_dz: {dx.value} {dy.value} {dz.value}\n")

        elif line.startswith("#domain"):
            new_lines.append(f"#domain: {domain_x.value} {domain_y.value} {domain_z.value}\n")

        elif line.startswith("#material"):
            new_lines.append(f"#material: {eps.value} {sigma.value} {mur.value} {sigma_m.value} {material_name.value}\n")

        elif line.startswith("#waveform"):
            new_lines.append(f"#waveform: gaussian {amplitude.value} {frequency.value} {waveform_name.value}\n")

        elif line.startswith("#hertzian_dipole"):
            new_lines.append(
                f"#hertzian_dipole: {direction.value} {src_x.value} {src_y.value} {src_z.value} {waveform_name.value}\n"
            )

        elif line.startswith("#rx"):
            new_lines.append(
                f"#rx: {rx_x.value} {rx_y.value} {rx_z.value}\n"
            )

        else:
            new_lines.append(line)


    new_file = "temp_bscan.in"

    with open(new_file, "w") as f:
        f.writelines(new_lines)


    cmd = f"python -m gprMax {new_file} -n {n}"

    print("Running:", cmd)

    #subprocess.run(cmd, shell=True)
    _ = subprocess.run(cmd, shell=True)

    return new_file, n
    

#Here we are merging filed using the predefined function to build upon existing architeture

@app.cell
def _(new_file):

    from tools.outputfiles_merge import merge_files

    base = new_file.replace(".in", "")

    print("Merging outputs")

    merge_files(base, removefiles=True)

    merged_file = base + "_merged.out"

    return merged_file


@app.cell
def _(merged_file, np,field_component):
    import h5py

    _f = h5py.File(merged_file, "r")

    rxnumber = len(_f["rxs"])
    dt = _f.attrs["dt"]

    data = []

    field = field_component.value

    for i in range(1, rxnumber + 1):
        data.append(_f[f"rxs/rx{i}/{field}"][:])

    data = np.array(data).T

    return data, dt, rxnumber, field

#here we are plotting using PREDEFINED FUNCTION to build upon existing architeture. 

@app.cell
def _(merged_file, data, dt, rxnumber,field):

    from tools.plot_Bscan import mpl_plot
    import matplotlib.pyplot as plt
    
    plt = mpl_plot(merged_file, data, dt, rxnumber, field)

    fig = plt.gcf()

    fig


app.run()