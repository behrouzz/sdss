**Author:** [Behrouz Safari](https://behrouzz.github.io/)<br/>
**License:** [MIT](https://opensource.org/licenses/MIT)<br/>

# sdss
*A python package for retrieving and analysing data from SDSS (Sloan Digital Sky Survey)*


## Installation

Install the latest version of *sdss* from [PyPI](https://pypi.org/project/sdss/):

    pip install sdss

Requirements are *numpy*, *requests*, *Pillow*, *matplotlib*, *pandas* and *astropy*.
Versions before 1.0.0 are not dependent on *astropy*.

## Quick start

Let's create a Region:

```python
from sdss import Region

ra = 179.689293428354
dec = -0.454379056007667

reg = Region(ra, dec, fov=0.033)
```

To see the image:

```python
reg.show()
```

![alt text](https://raw.githubusercontent.com/behrouzz/astronomy/main/images/Region-show.png)

To see the image in three *gri* filter bands (green, red, infrared) separately:

```python
reg.show3b()
```

![alt text](https://raw.githubusercontent.com/behrouzz/astronomy/main/images/Region-show3b.png)

To find nearest objects:

```python
df_obj = reg.nearest_objects()
```

To find nearest objects with spectrum:

```python
df_sp = reg.nearest_spects()
```

## Photometry example

Let's download a frame, in fits and jpg, retrieve all of its objects and then plot our target image.

```python
import matplotlib.pyplot as plt
from sdss.photometry import *


objid = 1237646587710014999

zip_adr = 'data/' + frame_filename(objid) + '.fits.bz2'
fits_adr = zip_adr[:-4]
jpg_adr = fits_adr.replace('-r-', '-irg-').replace('fits', 'jpg')

zip_url = obj_frame_url(objid, 'r')
download_file(zip_url, 'data/')
unzip(zip_adr)

jpg_url = obj_frame_url(objid, 'irg', jpg=True)
download_file(jpg_url, 'data/')

df = get_df(objid)
df = df_radec2pixel(df=df, fits_file=fits_adr)

img = obj_from_jpg(jpg_file=jpg_adr, df=df, objid=objid)

fig, ax = plt.subplots()
ax.imshow(img)
plt.show()
```

See more examples at [astrodatascience.net](https://astrodatascience.net/)
