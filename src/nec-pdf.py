#!/usr/bin/python
import gi
from gi.repository import Nautilus, GObject
from PyPDF2 import PdfFileReader as from_pdf

try:
    gi.require_version('Nautilus', '3.0')
except ValueError:
    gi.require_version('Nautilus', '4.0')
    from urllib.parse import unquote

class NecPdf(GObject.GObject,
             Nautilus.ColumnProvider,
             Nautilus.InfoProvider, ):

    nec_name = 'nec-pdf.py'

    mime_do = [
        'application/pdf'
    ]

    columns_setup = [
        {
            'name':        "NautilusPython::nec_pdf_title_column",
            'attribute':   "pdf_title",
            'label':       "PDF Title",
            'description': "PDF title",
        },
        {
            'name':        "NautilusPython::nec_pdf_artist_column",
            'attribute':   "pdf_artist",
            'label':       "PDF Artist",
            'description': "PDF Artist",
        },
        {
            'name':        "NautilusPython::nec_pdf_creator_column",
            'attribute':   "pdf_creator",
            'label':       "PDF Creator",
            'description': "PDF Creator",
        },
        {
            'name':        "NautilusPython::nec_pdf_producer_column",
            'attribute':   "pdf_producer",
            'label':       "PDF Producer",
            'description': "PDF Producer",
        },
        {
            'name':        "NautilusPython::nec_pdf_subject_column",
            'attribute':   "pdf_subject",
            'label':       "PDF Subject",
            'description': "PDF Subject",
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
                self.do_pypdf,
                provider,
                handle,
                closure,
                file_info,
                )

            return Nautilus.OperationResult.IN_PROGRESS

        return Nautilus.OperationResult.COMPLETE

    def do_pypdf(self, provider, handle, closure, file_info):
        filename = file_info.get_location().get_path() \
            if gi.get_required_version('Nautilus') == '3.0' \
            else unquote(file_info.get_uri()[7:])

        try:
            MapPyPDF2(filename).to(
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
            closure, provider, handle, Nautilus.OperationResult.COMPLETE, )

        return False


class MapPyPDF2:
    def __init__(self, filename):
        with open(filename, "rb") as f:
            i = from_pdf(f).getDocumentInfo()

        self.map(i)

    def to(self, fun) -> None:
        for (k, v) in self.__dict__.items():
            fun(k, v)

    def map(self, i) -> None:
        if v := getattr(i, 'author', None):
            self.pdf_artist = v

        if v := getattr(i, 'title', None):
            self.pdf_title = v

        if v := getattr(i, 'creator', None):
            self.pdf_creator = v

        if v := getattr(i, 'producer', None):
            self.pdf_producer = v

        if v := getattr(i, 'subject', None):
            self.pdf_subject = v
