#!/usr/bin/python
import gi
from gi.repository import Nautilus, GObject
from urllib.parse import unquote as uri_unescape
from pyexiv2 import ImageMetadata as from_exiv

gi.require_version('Nautilus', '3.0')


class NecExif(GObject.GObject,
              Nautilus.ColumnProvider,
              Nautilus.InfoProvider, ):

    debug_mode = False

    mime_do = [
        'image/jpeg', 'image/png', 'image/pgf', 'image/gif', 'image/bmp',
        'image/webp', 'image/targa', 'image/tiff', 'image/x-ms-bmp',
        'image/jp2', 'application/postscript', 'application/rdf+xml',
        'image/x-photoshop',

        'image/x-exv', 'image/x-canon-cr2', 'image/x-canon-crw',
        'image/x-minolta-mrw', 'image/x-nikon-nef', 'image/x-pentax-pef',
        'image/x-panasonic-rw2', 'image/x-samsung-srw', 'image/x-olympus-orf',
        'image/x-fuji-raf'
    ]

    columns_setup = [
        {
            'name':        "NautilusPython::exif_datetime_original_column",
            'attribute':   "exif_datetime_original",
            'label':       "EXIF Dateshot",
            'description': "Exif photo capture date",
        },
        {
            'name':        "NautilusPython::exif_software_column",
            'attribute':   "exif_software",
            'label':       "EXIF Software",
            'description': "Exif software used to save image",
        },
        {
            'name':        "NautilusPython::exif_flash_column",
            'attribute':   "exif_flash",
            'label':       "EXIF flash",
            'description': "Exif flash mode",
        },
        {
            'name':        "NautilusPython::exif_pixeldimensions_column",
            'attribute':   "exif_pixeldimensions",
            'label':       "EXIF Image Size",
            'description': "Exif image size",
        },
    ]

    def __init__(self):
        print("* Starting nec-exif")
        pass

    def throw_bailout(self, name, filename):
        if self.debug_mode:
            raise Exception("{}: {} bailout here".format(filename, name))
        else:
            print("{}: {} bailout here (skipping)".format(filename, name))

    def get_columns(self):
        return [
            Nautilus.Column(
                name=col['name'],
                attribute=col['attribute'],
                label=col['label'],
                description=col['description']
            )
            for col in self.columns_setup
        ]

    def do_pyexiv2(self, provider, handle, closure, file_info, filename):
        try:
            metadata = from_exiv(filename)
            metadata.read()
        except Exception:
            file_info.invalidate_extension_info()

            Nautilus.info_provider_update_complete_invoke(
                closure, provider, handle, Nautilus.OperationResult.FAILED, )

            self.throw_bailout(name="pyexiv2", filename=filename)
            return False

        try:
            file_info.add_string_attribute(
                'exif_datetime_original',
                str(metadata['Exif.Photo.DateTimeOriginal'].raw_value), )
        except Exception:
            pass

        try:
            file_info.add_string_attribute(
                'exif_software',
                str(metadata['Exif.Image.Software'].raw_value), )
        except Exception:
            pass

        try:
            file_info.add_string_attribute(
                'exif_flash',
                str(metadata['Exif.Photo.Flash'].raw_value), )
        except Exception:
            pass

        try:
            file_info.add_string_attribute(
                'exif_pixeldimensions',
                "{}x{}".format(
                    metadata['Exif.Photo.PixelXDimension'].raw_value,
                    metadata['Exif.Photo.PixelYDimension'].raw_value, ))
        except Exception:
            pass

        file_info.invalidate_extension_info()

        Nautilus.info_provider_update_complete_invoke(
            closure, provider, handle, Nautilus.OperationResult.COMPLETE, )

        return False

    def update_file_info_full(self, provider, handle, closure, file_info):
        for col in self.columns_setup:
            file_info.add_string_attribute(col['attribute'], '')

        if file_info.get_uri_scheme() == 'file' and \
           file_info.get_mime_type() in self.mime_do:
            filename = uri_unescape(file_info.get_uri()[7:])

            GObject.idle_add(
                self.do_pyexiv2,
                provider,
                handle,
                closure,
                file_info,
                filename, )
            return Nautilus.OperationResult.IN_PROGRESS

        return Nautilus.OperationResult.COMPLETE
