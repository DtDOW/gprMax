import gprMax.gprMax
import sys
import io
import contextlib


def run_model(model):

    temp_file = "temp_model.in"

    with open(temp_file,"w") as f:
        f.writelines(model.to_in_file())

    sys.argv = ["gprMax", temp_file]

    log_stream = io.StringIO()

    with contextlib.redirect_stdout(log_stream):
        gprMax.gprMax.main()

    logs = log_stream.getvalue()

    return "temp_model.out", logs