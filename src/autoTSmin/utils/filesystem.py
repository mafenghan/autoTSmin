import shutil
from pathlib import Path

def copy_file(source, target):
    source = Path(source)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

def remove_file(filename):
    filename = Path(filename)
    if filename.exists():
        filename.unlink()

def cat_file(file1,file2,target):
    file1 = Path(file1)
    file2 = Path(file2)
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target,'w') as f:
        with open(file1,'r') as f1:
            f.write(f1.read())
        with open(file2,'r') as f2:
            f.write(f2.read())
