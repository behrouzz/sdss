from urllib.request import urlopen, urlretrieve
import matplotlib.pyplot as plt
from .utils import (decode_objid, decode_specid, sql2df, binimg2array,
                   img_cutout, show_spect, show_object)
from .refs import photo_types

class PhotoObj:
    def __init__(self, objID):
        
        self.objID = str(objID)
        
        dc = decode_objid(objID)
        self.sky_version = dc['version']
        self.rerun = dc['rerun']
        self.run = dc['run']
        self.camcol = dc['camcol']
        self.field = dc['field']
        self.id_in_field = dc['id_within_field']
        
        self.specObjID = None
        self.ra = None
        self.dec = None
        self.mag = None
        self.type = None
        self.dist2sel = None
        self.downloaded = False

    def download(self, get_image=False):
        script = "SELECT specObjID,ra,dec,u,g,r,i,z,type "
        script = script + f"FROM PhotoObj WHERE objID={self.objID}"
        df = sql2df(script)
        if len(df)>0:
            float_cols = ['ra','dec','u','g','r','i','z']
            df[float_cols] = df[float_cols].astype(float)
            self.specObjID = df['specObjID'].iloc[0]
            self.ra = df['ra'].iloc[0]
            self.dec = df['dec'].iloc[0]
            u = df['u'].iloc[0]
            g = df['g'].iloc[0]
            r = df['r'].iloc[0]
            i = df['i'].iloc[0]
            z = df['z'].iloc[0]
            self.mag = {'u':u, 'g':g, 'r':r, 'i':i, 'z':z}
            self.type = photo_types[df['type'].iloc[0]]
            if get_image:
                self.img_array = self.quick_image()
        self.downloaded = True

    def cutout_image(self, scale=0.1, width=300, height=300):
        if not self.downloaded:
            self.download()
        if self.ra is None:
            raise Exception('Photo object not found!')
        data = img_cutout(ra=self.ra, dec=self.dec, scale=scale,
                          width=width, height=height, opt='', query='')
        return data

    def show(self, scale=0.1, width=200, height=200):
        data = self.cutout_image(scale=scale, width=width, height=height)
        plt.imshow(data)
        plt.show()


class SpecObj:
    def __init__(self, specObjID):
        
        self.specObjID = str(specObjID)
        
        dc = decode_specid(specObjID)
        self.plate = dc['plate']
        self.fiberID = dc['fiber_id']
        self.mjd = dc['mjd']
        self.run2d = dc['run2d']
        
        self.bestObjID = None
        self.ra = None
        self.dec = None
        self.z = None
        self.zErr = None
        self.zWarning = None
        self.mainClass = None
        self.subClass = None
        self.img = None
        self.dist2sel = None
        self.downloaded = False
        
        # photoObjs:
        self.mag = None
        self.type = None
        self.run = None
        self.camcol = None
        self.field = None
        

    def download(self):
        script = f"""SELECT s.bestObjID, s.ra, s.dec, p.u, p.g, p.r, p.i, p.z, p.type,
        s.z AS redshift, s.zErr, s.zWarning, s.class, s.subClass, s.img
        FROM SpecObj AS s
        JOIN PhotoObj AS p ON s.bestObjID=p.objID
        WHERE s.specObjID={self.specObjID}"""
        df = sql2df(script)
        if len(df)>0:
            float_cols = ['ra','dec','u','g','r','i','z', 'redshift','zErr']
            df[float_cols] = df[float_cols].astype(float)
            self.bestObjID = df['bestObjID'].iloc[0]
            self.ra = df['ra'].iloc[0]
            self.dec = df['dec'].iloc[0]
            u = df['u'].iloc[0]
            g = df['g'].iloc[0]
            r = df['r'].iloc[0]
            i = df['i'].iloc[0]
            z = df['z'].iloc[0]
            self.mag = {'u':u, 'g':g, 'r':r, 'i':i, 'z':z}
            self.type = photo_types[df['type'].iloc[0]]
            self.z = df['redshift'].iloc[0]
            self.zErr = df['zErr'].iloc[0]
            self.zWarning = df['zWarning'].iloc[0]
            self.mainClass = df['class'].iloc[0]
            self.subClass = df['subClass'].iloc[0]
            self.img = df['img'].iloc[0]
        self.downloaded = True

    def show_spec(self, figsize=None):
        if not self.downloaded:
            self.download()
        if figsize is None:
            fig, ax = plt.subplots()
        else:
            fig, ax = plt.subplots(figsize=figsize)
        data = binimg2array(self.img)
        ax.imshow(data, cmap='gray')
        plt.show()

    def download_spec(self, path='', lite=True):
        run2d = str(self.run2d)
        plate = str(self.plate).zfill(4)
        mjd = str(self.mjd).zfill(5)
        fiber = str(self.fiberID).zfill(4)
        BASE = "https://dr16.sdss.org/sas/dr16/sdss/spectro/redux/"
        if lite:
            PAR = f"{run2d}/spectra/lite/{plate}/"
        else:
            PAR = f"{run2d}/spectra/{plate}/"
        filename = f"spec-{plate}-{mjd}-{fiber}.fits"
        URL = BASE + PAR + filename
        urlretrieve(URL, path+filename)
