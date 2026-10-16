"""Exercise the installed wheel's actual console entry point outside this checkout."""
import hashlib, json, os, pathlib, shutil, sqlite3, subprocess, sys, tempfile

SOURCE=pathlib.Path(__file__).absolute().parent
PYTHON=pathlib.Path(sys.argv[1]).absolute()  # Do not resolve a venv symlink to its base interpreter.
COMMAND=PYTHON.parent / ("capacity-cut-report.exe" if os.name=="nt" else "capacity-cut-report")
CASES=0
def run(args, expected=0, data=True):
    global CASES
    p=subprocess.run([str(COMMAND), *map(str,args)],cwd=WORK,text=True,capture_output=True,timeout=30)
    assert p.returncode==expected, (args,p.returncode,p.stdout,p.stderr)
    CASES+=1
    if expected==2:
        assert not p.stdout and p.stderr, (args,p.stdout,p.stderr)
        return None
    return json.loads(p.stdout) if data else p.stdout

with tempfile.TemporaryDirectory(prefix="installed-command-") as tmp:
    WORK=pathlib.Path(tmp)
    assert not WORK.is_relative_to(SOURCE)
    env=subprocess.run([str(PYTHON),"-c","import capacity_cut_report; print(capacity_cut_report.__file__)"],cwd=WORK,text=True,capture_output=True,check=True)
    installed=pathlib.Path(env.stdout.strip()).absolute()
    assert not installed.is_relative_to(SOURCE), installed
    assert installed.read_bytes()==(SOURCE/"capacity_cut_report.py").read_bytes()
    run(["--help"],data=False)
    shutil.copyfile(SOURCE/"example.json",WORK/"example.json")
    r=run(["example.json"],1)
    assert r["fulfilled"]==6 and r["shortfall"]==2 and r["certificate"]["cut_capacity"]==6
    d=json.loads((WORK/"example.json").read_text());d["links"].append({"pool":"B","task":"X"})
    (WORK/"example.json").write_text(json.dumps(d));r=run(["example.json"]);assert r["fulfilled"]==8
    for raw in ('{"pools":[],"pools":[],"tasks":[],"links":[]}', '{"pools":[],"tasks":[],"links":[],"other":0}', '{"pools":[{"id":"A","capacity":NaN}],"tasks":[],"links":[]}'):
        (WORK/"bad.json").write_text(raw);run(["bad.json"],2)
    d["pools"][0]["capacity"]=-1;(WORK/"bad.json").write_text(json.dumps(d));run(["bad.json"],2)
    (WORK/"bad.json").write_bytes(b"x"*(2*1024*1024+1));run(["bad.json"],2)
print(json.dumps({"installed_command":"capacity-cut-report","cases":CASES,"module_bytes_match_source":True,"outside_checkout":True,"python":subprocess.check_output([str(PYTHON),"--version"],text=True).strip()}))
