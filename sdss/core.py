from urllib.request import urlopen, urlretrieve
import matplotlib.pyplot as plt

class Images:
    def __init__(self, ra, dec, scale=0.396127, width=300, height=300, opt='GS', query=''):
        self.ra, self.dec = ra, dec
        self.scale = scale
        self.width = width
        self.height = height
        self.opt = opt
        self.query = query
        self.data = None
        self.loaded = False

    def create_url(self):
        BASE = "http://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg?"
        PAR = f"ra={self.ra}&dec={self.dec}&scale={self.scale}&width={self.width}&height={self.height}"
        OPT = "&opt="+self.opt if self.opt !='' else ''
        QRY = "&query="+self.query if self.query!='' else ''
        url = BASE + PAR + OPT + QRY
        return url

    def image_data(self):
        url = self.create_url()
        self.data = plt.imread(urlopen(url), format='jpeg')
        self.loaded = True

    def show(self, band='all'):
        if self.loaded==False:
            self.image_data()
        fig, ax = plt.subplots()
        if band=='u':
            ax.imshow(self.data[:,:,0], cmap='gray')
        elif band=='g':
            ax.imshow(self.data[:,:,1], cmap='gray')
        elif band=='r':
            ax.imshow(self.data[:,:,2], cmap='gray')
        else:
            ax.imshow(self.data)
        plt.show()

    def show_separated(self):
        if self.loaded==False:
            self.image_data()
        fig, axes = plt.subplots(1,3)
        axes[0].imshow(self.data[:,:,0], cmap='gray'); axes[0].set_title('u-band')
        axes[1].imshow(self.data[:,:,1], cmap='gray'); axes[1].set_title('g-band')
        axes[2].imshow(self.data[:,:,2], cmap='gray'); axes[2].set_title('r-band')
        plt.show()

