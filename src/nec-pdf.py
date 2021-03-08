#!/usr/bin/python
import gi
from gi.repository import Nautilus, GObject
from PyPDF2 import PdfFileReader as from_pdf

gi.require_version('Nautilus', '3.0')


class NecPdf(GObject.GObject,
             Nautilus.ColumnProvider,
             Nautilus.InfoProvider, ):

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
        print("* Starting nec-pdf.py")

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
        filename = file_info.get_location().get_path()

        try:
            f = open(filename, "rb")
            i = from_pdf(f).getDocumentInfo()

            if hasattr(i, 'author') and i.author is not None:
                file_info.add_string_attribute('pdf_artist', i.author)

            if hasattr(i, 'title') and i.title is not None:
                file_info.add_string_attribute('pdf_title', i.title)

            if hasattr(i, 'creator') and i.creator is not None:
                file_info.add_string_attribute('pdf_creator')

            if hasattr(i, 'producer') and i.producer is not None:
                file_info.add_string_attribute('pdf_producer')

            if hasattr(i, 'subject') and i.subject is not None:
                file_info.add_string_attribute('pdf_subject')

        except Exception:
            print("{}: nec-pdf bailout here (skipping)".format(filename))

        finally:
            f.close()

        file_info.invalidate_extension_info()

        Nautilus.info_provider_update_complete_invoke(
            closure, provider, handle, Nautilus.OperationResult.COMPLETE, )

        return False
