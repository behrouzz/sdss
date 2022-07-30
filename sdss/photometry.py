"""
photometry module
-----------------
Useful links:

Imaging data models:
https://www.sdss.org/dr12/imaging/imaging_access/

Frame data model:
https://data.sdss.org//datamodel/files/BOSS_PHOTOOBJ/frames/RERUN/RUN/CAMCOL/frame.html
"""

import bz2
import numpy as np
from .utils import decode_objid


def frames_url(run):
    BASE = 'https://data.sdss.org//sas/dr17/eboss/photoObj/frames/301/'
    run6 = str(run).zfill(6)
    url = BASE + run + f'/frames-run-{run6}.html'
    return url


def frame_url(run, camcol, field, band, rerun=301, dr=17):
    BASE = f"https://data.sdss.org/sas/dr{dr}/eboss/photoObj/frames/"
    run6 = str(run).zfill(6)
    field = str(field).zfill(4)
    url = BASE + \
    f"{rerun}/{run}/{camcol}/frame-{band}-{run6}-{camcol}-{field}.fits.bz2"
    return url


def obj_frame_url(objid, band):
    dc = decode_objid(objid)
    url = frame_url(run=dc['run'],
                    camcol=dc['camcol'],
                    field=dc['field'],
                    band=band)
    return url


def unzip(filename):
    with bz2.open(filename, 'rb') as f:
        content = f.read()
    with open(filename[:-4], 'wb') as f:
        f.write(content)

        
def flux_star(data, center, r_star):
    h, w = data.shape
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= r_star
    flux_matrix = np.multiply(data, mask)
    return flux_matrix


def flux_sky(data, center, r_star, r_sky):
    h, w = data.shape
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask1 = dist_from_center <= r_sky
    mask2 = dist_from_center > r_star
    mask = np.logical_and(mask1, mask2)
    flux_matrix = np.multiply(data, mask)
    return flux_matrix
