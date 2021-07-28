from urllib.request import urlopen, urlretrieve
import matplotlib.pyplot as plt
from .utils import (decode_objid, decode_specid, sql2df, binimg2array,
                    img_cutout, show_spect, show_object)


class Region:
    # fov in degrees
    def __init__(self, ra, dec, fov=0.033, width=300, height=300, opt='GS', query=''):
        self.ra, self.dec = ra, dec
        self.fov = fov
        self.width = width
        self.height = height
        self.opt = opt
        self.query = query
        self.data = None
    
    def download_data(self):
        scale = self.fov * (0.396127 / 0.033)
        self.data = img_cutout(ra=self.ra, dec=self.dec, scale=scale, 
                               width=self.width, height=self.height,
                               opt=self.opt, query=self.query)

    def show(self, band='all', figsize=None):
        if self.data is None:
            self.download_data()
        if isinstance(figsize, tuple) and len(figsize)==2:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig, ax = plt.subplots()
        if band=='i':
            ax.imshow(self.data[:,:,0], cmap='gray')
        elif band=='r':
            ax.imshow(self.data[:,:,1], cmap='gray')
        elif band=='g':
            ax.imshow(self.data[:,:,2], cmap='gray')
        else:
            ax.imshow(self.data)
        plt.show()

    def show3b(self, figsize=None):
        if self.data is None:
            self.download_data()
        if isinstance(figsize, tuple) and len(figsize)==2:
            fig, axes = plt.subplots(1,3, figsize=figsize)
        else:
            fig, axes = plt.subplots(1,3)
        filters = ['green (g)', 'red (r)', 'infrared (i)']
        for i in range(len(filters)):
            axes[i].imshow(self.data[:,:,2-i], cmap='gray')
            axes[i].set_title(filters[i])
            axes[i].axis('off')
        plt.show()
    
    def nearest_objects(self, radius=None, n_max=1000, max_g=None):
        """
        radius : arcmin
        """
        if radius is None:
            radius = (self.fov * 60) /2
        max_g = f"WHERE p.g<{max_g}" if max_g is not None else ""
        scrip = f"""SELECT TOP {n_max} f.objID, f.type, f.distance,
        p.specObjID, p.ra, p.dec, p.u, p.g, p.r, p.i, p.z
        FROM dbo.fGetNearbyObjAllEq({self.ra},{self.dec},{radius}) AS f
        JOIN PhotoObj AS p ON p.objID = f.objID {max_g}
        ORDER BY f.distance"""
        df = sql2df(scrip)
        float_cols = ['distance','ra','dec','u','g','r','i','z']
        df[float_cols] = df[float_cols].astype(float)
        return df

    def nearest_spects(self, radius=None, n_max=1000):
        """
        radius : arcmin
        """
        if radius is None:
            radius = (self.fov * 60) /2
        scrip = f"""SELECT TOP {n_max} 
        sp.objID, f.specObjID, f.distance, sp.ra, sp.dec, sp.class, sp.subClass,
        sp.modelMag_u AS u, sp.modelMag_g AS g, sp.modelMag_r AS r, sp.modelMag_i AS i, sp.modelMag_z AS z, 
        f.z AS redshift, f.zErr, f.zWarning
        FROM dbo.fGetNearbySpecObjEq({self.ra},{self.dec},{radius}) AS f
        JOIN SpecPhoto AS sp ON sp.specObjID = f.specObjID
        ORDER BY f.distance"""
        df = sql2df(scrip)
        float_cols = ['distance','ra','dec','u','g','r','i','z','redshift','zErr']
        df[float_cols] = df[float_cols].astype(float)
        return df

