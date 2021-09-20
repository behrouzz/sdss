**Author:** [Behrouz Safari](https://behrouzz.github.io/)<br/>
**License:** [MIT](https://opensource.org/licenses/MIT)<br/>

# sdss
*A python package for retrieving and analysing data from SDSS (Sloan Digital Sky Survey)*


## Installation

Install the latest version of *sdss* from [PyPI](https://pypi.org/project/sdss/):

    pip install sdss

Requirements are *numpy*, *requests*, *Pillow*, *matplotlib* and *pandas*.


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

See more examples at [astrodatascience.net](https://astrodatascience.net/)
