# Nautilus extension: nautilus extra columns

Expand columns with extra data like: tags, metadata, exif, quality information.

# Instalation

Instalation can be selective, for eg: `make install-mediainfo` => `src/nec-mediainfo.py`

## Dependiences
* mediainfo: [pymediainfo](https://github.com/sbraz/pymediainfo/)
* exif: [pyexiv2](https://launchpad.net/py3exiv2)
* pdf: [PyPDF2](https://mstamy2.github.com/PyPDF2)

## To local destination (home directory)
``` bash
make install
```

## To global destination (system)

``` bash
make
sudo make install PREFIX=/usr
```

# Uninstalling

Append `un` to` install`
