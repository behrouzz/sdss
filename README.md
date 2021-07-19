**Author:** [Behrouz Safari](https://behrouzz.github.io/)<br/>
**License:** [MIT](https://opensource.org/licenses/MIT)<br/>

# sdss
*A python package for retrieving and analysing SDSS data*


## Installation

Install the latest version of *sdss* from [PyPI](https://pypi.org/project/sdss/):

    pip install sdss

Requirements are *numpy*, *pandas* and *matplotlib*.


## Quick start

Let's get the positions of the sun between two times:

```python
from sdss import Images

ra = 179.689293428354
dec = -0.454379056007667

img = Images(ra, dec)
img.show()
```
