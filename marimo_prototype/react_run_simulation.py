# react_run_simulation.py

from gprMax.gprMax import api as run
import io
import contextlib


def run_model(model):

    temp_file = "temp_model.in"

    # Write input file
    with open(temp_file, "w") as f:
        f.writelines(model.to_in_file())

    # Capture logs
    log_stream = io.StringIO()

    with contextlib.redirect_stdout(log_stream):
        run(
            inputfile=temp_file,
            n=1
        )

    logs = log_stream.getvalue()

    return "temp_model.out", logs