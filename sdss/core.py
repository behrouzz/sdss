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


class Object:
    def __init__(self, objID=None, specObjID=None):
        if objID is None and specObjID is None:
            raise Exception("You should enter 'objID' or 'specObjID'")
        
        self.objID = str(objID) if objID is not None else None
        self.specObjID = str(specObjID) if specObjID is not None else None
        self.ra = None
        self.dec = None
        self.u = None
        self.g = None
        self.r = None
        self.i = None
        self.z = None
        self.run = None
        self.camcol = None
        self.field = None
        self.type = None
        self.mjd = None
        self.plate = None
        self.fiberID = None
        self.redshift = None
        self.zErr = None
        self.zWarning = None
        self.mainClass = None
        self.subClass = None
        self.img = None

    def download(self):
        #if (self.objID is not None) and (self.specObjID is not None):
        #   self._download_obj_spect()
        if (self.objID is not None) and (self.specObjID is None):
            self._download_object()
        else:
            self._download_obj_spect()

    def _download_obj_spect(self):
        where = f"p.objID={self.objID}" if self.objID is not None else f"p.specObjID={self.specObjID}"
        script = f"""SELECT
        p.objID,p.specObjID,p.ra,p.dec,p.u,p.g,p.r,p.i,p.z,p.run,p.camcol,p.field,p.type,p.mjd,
        s.plate,s.fiberID,s.z AS redshift,s.zErr,s.zWarning,s.class,s.subClass,s.img
        FROM PhotoObj AS p
        JOIN SpecObj AS s ON s.bestObjID=p.objID
        WHERE """ + where
        df = sql2df(script)

        if (self.specObjID is not None) and (self.objID is not None):
            err1 = str(df['specObjID'].iloc[0])!=str(self.specObjID)
            err2 = str(df['objID'].iloc[0])!=str(self.objID)
            if err1 or err2:
                raise Exception("'objID' and 'specObjID' don't match!")

        if self.specObjID is not None:
            if str(df['specObjID'].iloc[0])!=str(self.specObjID):
                raise Exception("'objID' and 'specObjID' don't match!")
            else:
                self.objID = df['objID'].iloc[0]
                
        if self.objID is not None:
            if str(df['objID'].iloc[0])!=str(self.objID):
                raise Exception("'objID' and 'specObjID' don't match!")
            else:
                self.specObjID = df['specObjID'].iloc[0]

        if len(df)>0:
            int_cols = ['run','camcol','field','type','mjd','plate','fiberID','zWarning']
            float_cols = ['ra','dec','u','g','r','i','z','redshift','zErr']
            df[int_cols] = df[int_cols].astype(int)
            df[float_cols] = df[float_cols].astype(float)
            self.ra = df['ra'].iloc[0]
            self.dec = df['dec'].iloc[0]
            self.u = df['u'].iloc[0]
            self.g = df['g'].iloc[0]
            self.r = df['r'].iloc[0]
            self.i = df['i'].iloc[0]
            self.z = df['z'].iloc[0]
            self.run = df['run'].iloc[0]
            self.camcol = df['camcol'].iloc[0]
            self.field = df['field'].iloc[0]
            self.type = df['type'].iloc[0]
            self.mjd = df['mjd'].iloc[0]
            self.plate = df['plate'].iloc[0]
            self.fiberID = df['fiberID'].iloc[0]
            self.redshift = df['redshift'].iloc[0]
            self.zErr = df['zErr'].iloc[0]
            self.zWarning = df['zWarning'].iloc[0]
            self.mainClass = df['class'].iloc[0]
            self.subClass = df['subClass'].iloc[0]
            self.img = df['img'].iloc[0]
        
    def _download_object(self):
        script = "SELECT objID,specObjID,ra,dec,u,g,r,i,z,run,camcol,field,type,mjd "
        script = script + f"FROM PhotoObj WHERE objID={self.objID}"
        df = sql2df(script)
        if len(df)>0:
            int_cols = ['run','camcol','field','type','mjd']
            float_cols = ['ra','dec','u','g','r','i','z']
            df[int_cols] = df[int_cols].astype(int)
            df[float_cols] = df[float_cols].astype(float)
            self.specObjID = df['specObjID'].iloc[0]
            self.ra = df['ra'].iloc[0]
            self.dec = df['dec'].iloc[0]
            self.u = df['u'].iloc[0]
            self.g = df['g'].iloc[0]
            self.r = df['r'].iloc[0]
            self.i = df['i'].iloc[0]
            self.z = df['z'].iloc[0]
            self.run = df['run'].iloc[0]
            self.camcol = df['camcol'].iloc[0]
            self.field = df['field'].iloc[0]
            self.type = df['type'].iloc[0]
            self.mjd = df['mjd'].iloc[0]

            if self.specObjID!='0':
                self._download_spect()

    def _download_spect(self):
        script = "SELECT plate,fiberID,z AS redshift,zErr,zWarning,class,subClass,img "
        script = script + f"FROM SpecObj WHERE specObjID={self.specObjID}"
        df = sql2df(script)
        if len(df)>0:
            self.plate = df['plate'].iloc[0]
            self.fiberID = df['fiberID'].iloc[0]
            self.redshift = df['redshift'].iloc[0]
            self.zErr = df['zErr'].iloc[0]
            self.zWarning = df['zWarning'].iloc[0]
            self.mainClass = df['class'].iloc[0]
            self.subClass = df['subClass'].iloc[0]
            self.img = df['img'].iloc[0]
