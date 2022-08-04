"""
photometry module
-----------------
Module for download image from SDSS server and photometric calculations.

Useful links:

Imaging data models:
https://www.sdss.org/dr12/imaging/imaging_access/

Frame data model:
https://data.sdss.org//datamodel/files/BOSS_PHOTOOBJ/frames/RERUN/RUN/CAMCOL/frame.html
"""

import bz2, requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
from .utils import decode_objid, sql2df


def download_file(url, path=''):
    filename = url.rsplit('/', 1)[-1]
    r = requests.get(url, allow_redirects=True)
    open(path+filename, 'wb').write(r.content)


def frame_filename(objid):
    dc = decode_objid(objid)
    run6 = str(dc['run']).zfill(6)
    camcol = dc['camcol']
    field = str(dc['field']).zfill(4)
    filename = f'frame-r-{run6}-{camcol}-{field}'
    return filename

def get_df(objid):
    dc = decode_objid(objid)

    script = f"""
    SELECT objid, ra, dec, i, r, g
    FROM PhotoObj
    WHERE run={dc['run']}
    AND camcol={dc['camcol']}
    AND field={dc['field']}
    """

    df = sql2df(script)
    df['objid'] = df['objid'].astype('int64')
    df[['ra','dec','i','r','g']] = df[['ra','dec','i','r','g']].astype(float)
    
    return df


def df_radec2pixel(df, fits_file):
    
    hdul = fits.open(fits_file)
    img = hdul[0].data
    wcs = WCS(hdul[0].header)
    hdul.close()

    coords = SkyCoord(ra=df['ra'], dec=df['dec'], unit='deg')
    ls_ra_px = []
    ls_dec_px = []

    for c in coords:
        ra_px, dec_px = wcs.world_to_pixel(c)
        ls_ra_px.append(float(ra_px))
        ls_dec_px.append(float(dec_px))

    df['ra_px'] = ls_ra_px
    df['dec_px'] = ls_dec_px

    return df


def obj_from_jpg(jpg_file, df, objid, n=50):

    jpg = plt.imread(jpg_file)

    jpg0 = jpg[:, :, 0]
    jpg1 = jpg[:, :, 1]
    jpg2 = jpg[:, :, 2]

    jpg0 = jpg0[::-1, :]
    jpg1 = jpg1[::-1, :]
    jpg2 = jpg2[::-1, :]

    df['xlim1'] = df['ra_px'].apply(round) - n
    df['xlim2'] = df['ra_px'].apply(round) + n
    df['ylim1'] = df['dec_px'].apply(round) - n
    df['ylim2'] = df['dec_px'].apply(round) + n

    obj_df = df[df['objid']==objid]

    xlim1 = obj_df['xlim1'].iloc[0]
    xlim2 = obj_df['xlim2'].iloc[0]
    ylim1 = obj_df['ylim1'].iloc[0]
    ylim2 = obj_df['ylim2'].iloc[0]

    img_cut0 = jpg0[ylim1:ylim2, xlim1:xlim2]
    img_cut1 = jpg1[ylim1:ylim2, xlim1:xlim2]
    img_cut2 = jpg2[ylim1:ylim2, xlim1:xlim2]

    img = np.zeros((img_cut1.shape[0], img_cut1.shape[1], 3))
    img[:,:, 0] = img_cut0
    img[:,:, 1] = img_cut1
    img[:,:, 2] = img_cut2

    return img.astype(int)


def frames_url(run):
    BASE = 'https://data.sdss.org//sas/dr17/eboss/photoObj/frames/301/'
    run6 = str(run).zfill(6)
    url = BASE + run + f'/frames-run-{run6}.html'
    return url


def frame_url(run, camcol, field, band, rerun=301, dr=17, jpg=False):
    BASE = f"https://data.sdss.org/sas/dr{dr}/eboss/photoObj/frames/"
    run6 = str(run).zfill(6)
    field = str(field).zfill(4)
    url = BASE + \
    f"{rerun}/{run}/{camcol}/frame-{band}-{run6}-{camcol}-{field}.fits.bz2"
    if jpg:
        url = url.replace(f'-{band}-', '-irg-')
        url = url.replace('fits.bz2', 'jpg')
    return url


def obj_frame_url(objid, band, jpg=False):
    dc = decode_objid(objid)
    url = frame_url(run=dc['run'],
                    camcol=dc['camcol'],
                    field=dc['field'],
                    band=band,
                   jpg=jpg)
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
