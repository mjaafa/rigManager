from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

import psutil

LOG = logging.getLogger(__name__)


@dataclass(slots=True)
class ManagedProcess:
    command: list[str]
    process: subprocess.Popen[str]


class ProcessManager:
    def __init__(self) -> None:
        self.current: ManagedProcess | None = None

    def start(self, command: list[str]) -> ManagedProcess:
        if self.current is not None:
            self.stop()
        executable = Path(command[0])
        cwd = str(executable.parent) if executable.parent.exists() else None
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.current = ManagedProcess(command=command, process=process)
        LOG.info("Started miner process with PID %s", process.pid)
        return self.current

    def is_alive(self) -> bool:
        return self.current is not None and self.current.process.poll() is None

    def stop(self) -> None:
        if self.current is None:
            return
        process = self.current.process
        try:
            parent = psutil.Process(process.pid)
            children = parent.children(recursive=True)
            for child in children:
                child.terminate()
            parent.terminate()
            _, alive = psutil.wait_procs([parent, *children], timeout=10)
            for item in alive:
                item.kill()
        except psutil.Error:
            process.terminate()
        finally:
            self.current = None
