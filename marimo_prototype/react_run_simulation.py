#react
import gprMax.gprMax
import sys
import io
import contextlib
import marimo as mo
import re

_ansi = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

class _LiveLogStream(io.StringIO):
    """Writes to gprMax stdout AND streams cleaned lines to mo.output live."""
    def __init__(self):
        super().__init__()
        self._log = ""
        
    def write(self, text):
        clean = _ansi.sub('', text)

        # Handle carriage return (progress bars)
        if '\r' in clean:
            # overwrite last line instead of appending
            parts = clean.split('\r')
            self._log = self._log.rsplit('\n', 1)[0] + '\n' + parts[-1]
        else:
            self._log += clean

        mo.output.replace(_render_log(self._log))
        return super().write(text)

    def flush(self):
        pass


def _render_log(text: str):
    return mo.Html(f"""
<div style="
  background:#0f172a; color:#e5e7eb;
  font-family:monospace; font-size:12px;
  padding:12px; border-radius:8px;
  height:400px; overflow-y:auto;
">
  <b style="color:#60a5fa">gprMax Simulation Logs</b>
  <hr style="border-color:#374151; margin:6px 0;">
  <pre style="margin:0; white-space:pre-wrap;">{text}</pre>
</div>
""")


def run_model(model):
    temp_file = "temp_model.in"

    with open(temp_file, "w") as f:
        f.writelines(model.to_in_file())

    sys.argv = ["gprMax", temp_file]

    stream = _LiveLogStream()

    with contextlib.redirect_stdout(stream):
        gprMax.gprMax.main()

    return "temp_model.out", stream.getvalue()