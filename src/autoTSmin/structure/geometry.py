import numpy as np
from math import pi, sqrt, sin, cos

def latt2abc(latt):
    abc = np.zeros((6))
    abc[0] = np.linalg.norm(latt[0,:])
    abc[1] = np.linalg.norm(latt[1,:])
    abc[2] = np.linalg.norm(latt[2,:])
    ua = (latt[0,:]/abc[0])
    ub = (latt[1,:]/abc[1])
    uc = (latt[2,:]/abc[2])
    abc[3] = 180.0/pi*np.arccos(np.dot(ub,uc))
    abc[4] = 180.0/pi*np.arccos(np.dot(ua,uc))
    abc[5] = 180.0/pi*np.arccos(np.dot(ua,ub))
    return abc

def abc2latt(abc):
    a = abc[0]
    b = abc[1]
    c = abc[2]
    alf = abc[3]
    bet = abc[4]
    gam = abc[5]
    abc_latt = np.zeros((3,3))
    abc_latt[0,0] = a
    abc_latt[1,0] = b*cos(gam*pi/180.0)
    abc_latt[1,1] = b*sin(gam*pi/180.0)
    abc_latt[2,0] = c*cos(bet*pi/180.0)
    abc_latt[2,1] = (b*c*cos(alf*pi/180.0)-abc_latt[1,0]*abc_latt[2,0])/abc_latt[1,1]
    abc_latt[2,2] = sqrt(c**2-abc_latt[2,0]**2-abc_latt[2,1]**2)
    return np.mat(abc_latt)

def dir2car(lattice,atomdir):
    atomcar = np.zeros((atomdir.shape[0],3))
    for i in range(atomdir.shape[0]):
        atomcar[i] = np.mat(atomdir[i,:])*np.mat(lattice)
    return np.array(atomcar)

def car2dir(lattice,atomcar):
    atomdir = np.mat(atomcar) * np.mat(lattice).I
    return np.array(atomdir)

def distance_matrix(row,col):
    a=row[["x","y","z"]].to_numpy(dtype=float); b=col[["x","y","z"]].to_numpy(dtype=float)
    return np.linalg.norm(b[:,None,:]-a[None,:,:],axis=2)

def distance_matrix_pbc(r,c,lattice):
    r_max_xyz = r[['x','y','z']].to_numpy(dtype=float).max()
    c_max_xyz = c[['x','y','z']].to_numpy(dtype=float).max()
    max_xyz = max(r_max_xyz, c_max_xyz)
    if max_xyz > 1.0:
        r_frac_coords = car2dir(lattice, r[['x','y','z']].to_numpy(dtype=float))
        c_frac_coords = car2dir(lattice, c[['x','y','z']].to_numpy(dtype=float))
    else:
        r_frac_coords = r[['x','y','z']].to_numpy(dtype=float)
        c_frac_coords = c[['x','y','z']].to_numpy(dtype=float)
    r_frac_coords = np.mod(r_frac_coords, 1.0)
    c_frac_coords = np.mod(c_frac_coords, 1.0)
    dist = []
    for i in range(c_frac_coords.shape[0]):
        delta = np.array(r_frac_coords - c_frac_coords[i,:],dtype = float)
        delta -= np.round(delta) # 去除周期性的影响
        dist.append(np.linalg.norm(np.dot(delta, lattice),axis = 1))
    return np.array(dist).T

def find_neighbors(distances,atom_index,cutoff,min_distance=0.5):
    v=distances[:,atom_index]; return [i for i,x in enumerate(v) if min_distance<x<cutoff]

