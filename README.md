**Author:** [Behrouz Safari](https://behrouzz.github.io/)<br/>
**License:** [MIT](https://opensource.org/licenses/MIT)<br/>

# sdss
*A python package for retrieving and analysing data from SDSS (Sloan Digital Sky Survey)*


## Installation

Install the latest version of *sdss* from [PyPI](https://pypi.org/project/sdss/):

    pip install sdss

Requirements are *numpy*, *Pillow*, *matplotlib* and *pandas*.


## Quick start

Let's create a Region:

```python
from sdss import Region

ra = 179.689293428354
dec = -0.454379056007667

img = Region(ra, dec, fov=0.033)
```

To see the image:

```python
img.show()
```

![alt text](https://raw.githubusercontent.com/behrouzz/astronomy/main/images/Region-show.png)

To see the image in three *gri* filter bands (green, red, infrared) separately:

```python
img.show3b()
```

![alt text](https://raw.githubusercontent.com/behrouzz/astronomy/main/images/Region-show3b.png)

To find 10 nearest objects in a radius of 5 arc degrees:

```python
df_obj = img.nearest_objects(radius=5, n=10)
```

To find 10 nearest objects with spectrum in a radius of 5 arc degrees:

```python
df_sp = img.nearest_spects(radius=5, n=10)
```
