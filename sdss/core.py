from urllib.request import urlopen, urlretrieve
import matplotlib.pyplot as plt
from .utils import sql2df, binimg2array, img_cutout, show_spect, show_object


class Region:
    def __init__(self, ra, dec, scale=0.396127, width=300, height=300, opt='GS', query=''):
        self.ra, self.dec = ra, dec
        self.scale = scale
        self.width = width
        self.height = height
        self.opt = opt
        self.query = query
        self.data = None
    
    def download_data(self):
        self.data = img_cutout(ra=self.ra, dec=self.dec, scale=self.scale, 
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
    
    def nearest_objects(self, radius, n=10):
        """
        radius : arcmin
        """
        SQL = f"SELECT TOP {n} objID,run,camcol,field,type,htmID,distance "
        SQL = SQL + f"FROM dbo.fGetNearbyObjAllEq({self.ra},{self.dec},{radius}) ORDER BY distance"
        df = sql2df(SQL)
        df.iloc[:,1:-1] = df.iloc[:,1:-1].astype(int)
        df.iloc[:,-1] = df.iloc[:,-1].astype(float)
        return df

    def nearest_spects(self, radius, n=10):
        """
        radius : arcmin
        """
        SQL = f"""SELECT TOP {n} 
        f.specObjID, sp.objID, sp.ra, sp.dec, sp.class, sp.subClass,
        sp.run, sp.camcol, sp.field,
        sp.modelMag_u AS u, sp.modelMag_g AS g, sp.modelMag_r AS r, sp.modelMag_i AS i, sp.modelMag_z AS z, 
        f.plate, f.mjd, f.fiberID, f.z AS redshift, f.zErr, f.zWarning, f.htmID, f.distance
        FROM dbo.fGetNearbySpecObjEq({self.ra},{self.dec},{radius}) AS f
        JOIN SpecPhoto AS sp ON sp.specObjID = f.specObjID
        ORDER BY f.distance"""
        df = sql2df(SQL)
        int_cols = ['run','camcol','field','plate','mjd','fiberID','zWarning','htmID']
        float_cols = ['ra','dec','u','g','r','i','z','redshift','zErr','distance']
        df[int_cols] = df[int_cols].astype(int)
        df[float_cols] = df[float_cols].astype(float)
        return df
