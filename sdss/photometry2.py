from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from astropy.coordinates import SkyCoord
import pandas as pd
from sdss.utils import decode_objid
from sdss import sql2df
from sdss.photometry import obj_frame_url, unzip


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


#==============================================================

objid = 1237646587710014999

zip_adr = 'data/' + frame_filename(objid) + '.fits.bz2'
fits_adr = zip_adr[:-4]
jpg_adr = fits_adr.replace('-r-', '-irg-').replace('fits', 'jpg')

should_download = False # we have already downloaded files

if should_download:
    zip_url = obj_frame_url(objid, 'r')
    urlretrieve(zip_url, zip_adr)
    unzip(zip_adr)
    jpg_url = obj_frame_url(objid, 'irg', jpg=True)
    urlretrieve(jpg_url, jpg_adr)

df = get_df(objid)
df = df_radec2pixel(df=df, fits_file=fits_adr)

img = obj_from_jpg(jpg_file=jpg_adr, df=df, objid=objid)

fig, ax = plt.subplots()
ax.imshow(img)
plt.show()


