import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sdss",
    version="0.2.0",
    author="Behrouz Safari",
    author_email="behrouz.safari@gmail.com",
    description="A python package for retrieving and analysing data from SDSS (Sloan Digital Sky Survey)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/behrouzz/sdss",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["sdss"],
    include_package_data=True,
    install_requires=["numpy", "requests", "Pillow", "matplotlib", "pandas"],
    python_requires='>=3.4',
)
