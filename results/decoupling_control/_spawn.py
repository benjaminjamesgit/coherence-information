"""Detach the decoupling-control runner into its own session (macOS has no `setsid` CLI).

Fork; the parent exits immediately so the launching shell / Bash tool returns at once. The
child calls os.setsid() (new session, no controlling terminal -> immune to SIGHUP and to the
harness reaping the original process group), redirects std fds to daemon.log, and execs the
runner, which thus becomes a fully detached, init-reparented session leader running ~2.7h.
"""
import os

REPO = "/Users/benjamin/Projects/coherence-information"
D = REPO + "/results/decoupling_control"

if os.fork() > 0:
    os._exit(0)                      # parent returns control to the shell immediately

os.setsid()                          # child: brand-new session, no controlling tty
os.chdir(REPO)

devnull = os.open(os.devnull, os.O_RDONLY)
log = os.open(D + "/daemon.log", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
os.dup2(devnull, 0)
os.dup2(log, 1)
os.dup2(log, 2)

os.execvp("sh", ["sh", D + "/_runner.sh"])
