from pathlib import Path
from importlib_metadata import files
import pandas as pd
import re
from .geometry import distance_matrix_pbc

class arcread():
    def __init__(self,filelist,sort = False):
        PT_PATH = Path(__file__).parent / "PeriodicTable.csv"
        PT = pd.read_csv(PT_PATH, index_col=0)
        self.arc = []
        for i in filelist:
            if 'CORE' in i or 'MOL' in i:
                a = i.split()
                atomtype = re.split(r'\d+', a[0])[0]
                if atomtype == 'xx' or '_' in atomtype:
                    atomtype = a[-2]
                self.arc.append([atomtype,PT.loc[atomtype,'number'],float(a[1]),float(a[2]),float(a[3]),int(a[5])])
            elif 'PBC  ' in i:
                a = i.split()
                self.abc = [float(a[1]),float(a[2]),float(a[3]),float(a[4]),float(a[5]),float(a[6])]
            elif 'Energy' in i:
                a = i.split()
                try:
                    self.en =  float(a[3])
                except:
                    self.en =  0.0
        self.arc = pd.DataFrame(self.arc,columns=['type','number','x','y','z','charge'])
        if 0 not in self.arc['charge']:
            self.arc['charge'] = [0] * self.arc.shape[0]
        if sort == True:
            self.arc.sort_values(by=['number','z'],inplace = True,ascending = [False,True],ignore_index = True)

    def atominfo(self):
        self.atomtype, self.atomnumber = [], []
        for i in self.arc.index:
            if self.arc.loc[i,'type'] not in self.atomtype:
                self.atomtype.append(self.arc.loc[i,'type'])
                self.atomnumber.append(1)
            else:
                self.atomnumber[-1] += 1

def read_arc(path_or_lines):
    if isinstance(path_or_lines,(str,Path)):
        path_or_lines=Path(path_or_lines).read_text(encoding="utf-8").splitlines()
    return arcread(path_or_lines)

def write_arc(arc,abc,filename,sort=False):
    data=arc.copy()
    if sort:
        data=data.sort_values(by=["number","z"],ascending=[False,True])
    out=Path(filename); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8") as f:
        f.write("!BIOSYM archive 2\nPBC=ON\n         Energy   0    0      0.000000\n!DATE\n")
        f.write("PBC   %12.6f %12.6f %12.6f %12.6f %12.6f %12.6f\n"%tuple(abc[:6]))
        for n,(_,r) in enumerate(data.iterrows(),1):
            t=str(r["type"]); fmt=("%s %18.9f %14.9f %14.9f %s %4s %2s %2s %4s %4s\n" if len(t)==1 else "%s %17.9f %14.9f %14.9f %s %4s %2s %2s %4s %4s\n")
            f.write(fmt%(t,r["x"],r["y"],r["z"],"CORE",n,t,t,"0.0000",n))
        f.write("end\nend\n")

def split_arc(path_or_lines):
    if isinstance(path_or_lines,(str,Path)):
        path_or_lines=Path(path_or_lines).read_text(encoding="utf-8").splitlines()
    end = [k for k,v in enumerate(path_or_lines) if 'end' in v]
    end = [end[i] for i in range(1,len(end),2)]
    arclist = []
    for i in range(len(end)):
        if i == 0:          arclist.append(path_or_lines[0:end[i]+1])
        else:               arclist.append(path_or_lines[end[i-1]+1:end[i]+1])
    return arclist

def get_lowest_energy_structure(all_arc):
    arclist = split_arc(all_arc)
    enlist = []
    for i in arclist:
        a = arcread(i)
        enlist.append(a.en)
    min_index = enlist.index(min(enlist))
    return arcread(arclist[min_index])

def check_bond_relation(is_file, fs_file, atom_i, atom_j):
    _is = read_arc(is_file)
    _fs = read_arc(fs_file)
    is_distances = distance_matrix_pbc(_is.arc.loc[atom_i:atom_i,:], _is.arc.loc[atom_j:atom_j,:], abc=_is.abc)
    fs_distances = distance_matrix_pbc(_fs.arc.loc[atom_i:atom_i,:], _fs.arc.loc[atom_j:atom_j,:], abc=_fs.abc)
    is_dist = is_distances[0,0]
    fs_dist = fs_distances[0,0]
    if is_dist < 1.5 and fs_dist > 1.5:
        return True, "bond broken"
    elif is_dist > 1.5 and fs_dist < 1.5:
        return True, "bond formed"
    else:
        return False, "no change"
