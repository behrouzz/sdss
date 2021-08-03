from urllib.request import urlopen, urlretrieve
import requests
import matplotlib.pyplot as plt
import pandas as pd
import binascii, io, bz2, os
from PIL import Image
import numpy as np

def hmsdms_to_deg(hmsdms):
    """
    Convert HMS (hours, minutes, seconds) and DMS (degrees, minutes, seconds) to
    RA, DEC in decimal degrees.

    Example:
        hmsdms_to_deg('06 45 08.91728 -16 42 58.0171')
    Return:
        (101.28715533333333, -15.28388413888889)
    """
    ls = hmsdms.split(' ')
    ra_h = int(ls[0])
    ra_m = int(ls[1])
    ra_s = float(ls[2])
    dec_d = int(ls[3])
    dec_m = int(ls[4])
    dec_s = float(ls[5])

    ra = 15*ra_h + 15*ra_m/60 + 15*ra_s/3600
    dec = dec_d + dec_m/60 + dec_s/3600

    return ra, dec

def decode_objid(obj_id):
    if isinstance(obj_id, str):
        obj_id = int(obj_id)
    b = bin(obj_id)[2:].zfill(64)
    dc = {}
    dc['version'] = int(b[1:5], 2)
    dc['rerun'] = int(b[5:16], 2)
    dc['run'] = int(b[16:32], 2)
    dc['camcol'] = int(b[32:35], 2)
    dc['first_field'] = int(b[35], 2)
    dc['field'] = int(b[36:48], 2)
    dc['id_within_field'] = int(b[48:], 2)
    return dc

def decode_specid(spec_id):
    if isinstance(spec_id, str):
        spec_id = int(spec_id)
    b = bin(spec_id)[2:].zfill(64)
    dc = {}
    dc['plate'] = int(b[:14], 2)
    dc['fiber_id'] = int(b[14:26], 2)
    dc['mjd'] = int(b[26:40], 2) + 50000
    dc['run2d'] = int(b[40:54], 2)
    return dc

def sql2df(script):
    BASE = "http://skyserver.sdss.org/dr16/SkyServerWS/SearchTools/SqlSearch?cmd="
    script = ' '.join(script.strip().split('\n'))
    url = BASE+script.replace(' ', '%20') + '&format=csv'
    req = requests.request('GET', url)
    r = req.content.decode('utf-8')
    lines = r.splitlines()
    col = lines[1].split(',')
    data_lines = [i.split(',') for i in lines[2:]]
    return pd.DataFrame(data_lines, columns=col)

def sql_columns(table_name):
    script = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}'"
    df = sql2df(script)
    return list(df['COLUMN_NAME'])

def binimg2array(img_raw):
    img_raw = img_raw[2:]
    img_b = binascii.a2b_hex(img_raw)
    img = Image.open(io.BytesIO(img_b))
    data = np.array(img)
    return data

def img_cutout(ra, dec, scale, width, height, opt, query):
    BASE = "http://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg?"
    PAR = f"ra={ra}&dec={dec}&scale={scale}&width={width}&height={height}"
    OPT = "&opt="+opt if opt !='' else ''
    QRY = "&query="+query if query!='' else ''
    url = BASE + PAR + OPT + QRY
    data = plt.imread(urlopen(url), format='jpeg')
    return data

def show_spect(specObjID, figsize=(15,20)):
    url = f"http://skyserver.sdss.org/dr16/en/get/SpecById.ashx?id={specObjID}"
    data = plt.imread(urlopen(url), format='jpeg')
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(data)
    plt.show()

def show_object(objID, scale=0.1, width=300, height=300, figsize=(10,10)):
    script = f"SELECT TOP 1 ra,dec FROM PhotoObj WHERE objID={objID}"
    df = sql2df(script)
    ra, dec = df['ra'].iloc[0], df['dec'].iloc[0]
    data = img_cutout(ra, dec, scale=scale, width=width, height=height, opt='', query='')
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(data)
    plt.show()

def download_frame(field, run, camcol, band, fr_type='jpg', path=''):
    rerun = 301 #currently fixed
    zrun = str(run).zfill(6)
    zfield = str(field).zfill(4)
    
    if fr_type=='fits':
        filename = f"frame-{band}-{zrun}-{camcol}-{zfield}.fits.bz2"
    elif fr_type=='jpg':
        filename = f"frame-{band}-{zrun}-{camcol}-{zfield}.jpg"
    else:
        raise Exception("fr_type should be 'jpg' or 'fits'.")
    
    BASE = "https://data.sdss.org/sas/dr16/eboss/photoObj/frames/"
    url = BASE + f"{rerun}/{run}/{camcol}/" + filename
    urlretrieve(url, path+filename)
    
    if fr_type=='fits':
        with bz2.open(path+filename, 'rb') as f:
            content = f.read()
        with open(path+filename[:-4], 'wb') as f:
            f.write(content)
        os.remove(path+filename)
