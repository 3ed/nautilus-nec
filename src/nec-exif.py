#!/usr/bin/python
import gi
from gi.repository import Nautilus, GObject
from pyexiv2 import ImageMetadata as from_exiv

try:
    gi.require_version('Nautilus', '3.0')
except ValueError:
    gi.require_version('Nautilus', '4.0')


class NecExif(GObject.GObject,
              Nautilus.ColumnProvider,
              Nautilus.InfoProvider, ):

    nec_name = 'nec-exif.py'

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
        print("* Starting {}".format(self.nec_name))

    def get_columns(self):
        return [
            Nautilus.Column(
                name=col['name'],
                attribute=col['attribute'],
                label=col['label'],
                description=col['description']
            )
            for col in self.columns_setup]

    def update_file_info_full(self, provider, handle, closure, file_info):
        for col in self.columns_setup:
            file_info.add_string_attribute(col['attribute'], '')

        if file_info.get_uri_scheme() == 'file' and \
           file_info.get_mime_type() in self.mime_do:

            GObject.idle_add(
                self.do_event,
                provider,
                handle,
                closure,
                file_info,
                )

            return Nautilus.OperationResult.IN_PROGRESS

        return Nautilus.OperationResult.COMPLETE

    def do_event(self, provider, handle, closure, file_info) -> bool:
        filename = file_info.get_location().get_path()

        try:
            MapPyExiv2(filename).to(
                lambda k, v: file_info.add_string_attribute(k, v)
                )

        except Exception as error:
            print("--- ERROR in {} ---\nfile: {}\nmsg:  {}\n---".format(
                self.nec_name,
                filename,
                str(error),
                ))

        file_info.invalidate_extension_info()

        Nautilus.info_provider_update_complete_invoke(
            closure,
            provider,
            handle,
            Nautilus.OperationResult.COMPLETE,
            )

        return False


class MapPyExiv2:
    def __init__(self, filename) -> None:
        metadata = from_exiv(filename)
        metadata.read()

        self.map(metadata)

    def to(self, fun) -> None:
        for (k, v) in self.__dict__.items():
            fun(k, v)

    def map(self, i) -> None:
        if v := i.get('Exif.Photo.DateTimeOriginal'):
            self.exif_datetime_original = v.raw_value

        if v := i.get('Exif.Image.Software'):
            self.exif_software = v.raw_value

        if v := i.get('Exif.Photo.Flash'):
            self.exif_flash = v.raw_value

        if x := i.get('Exif.Photo.PixelXDimension'):
            if y := i.get('Exif.Photo.PixelYDimension'):
                self.exif_pixeldimensions = "{}x{}".format(
                    x.raw_value,
                    y.raw_value,
                    )
