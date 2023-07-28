#!/usr/bin/python
import gi
from gi.repository import Nautilus, GObject
from pymediainfo import MediaInfo

try:
    gi.require_version('Nautilus', '3.0')
except ValueError:
    gi.require_version('Nautilus', '4.0')


class NecMediainfo(GObject.GObject,
                   Nautilus.ColumnProvider,
                   Nautilus.InfoProvider, ):

    nec_name = 'nec-mediainfo.py'

    mime_do = [
        'audio/x-wav',

        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',

        'application/x-matroska', 'audio/x-matroska', 'video/x-matroska',

        'application/ogg', 'audio/ogg', 'audio/x-flac+ogg', 'audio/x-opus+ogg',
        'audio/x-speex+ogg', 'audio/x-vorbis+ogg', 'video/ogg',
        'video/x-ogm+ogg', 'video/x-theora+ogg',

        'audio/aac',

        'audio/flac',

        'audio/mp2', 'video/mp2t',

        'audio/mpeg', 'video/mpeg',

        'audio/mp4', 'video/mp4',

        'video/quicktime',

        'application/vnd.ms-asf', 'audio/x-ms-wma', 'video/x-ms-wmv',
        'video/x-msvideo',

        'application/vnd.rn-realmedia', 'audio/vnd.rn-realaudio',
        'video/vnd.rn-realvideo',

        'audio/x-ape',

        'audio/webm', 'video/webm',

        'video/x-flv',
    ]

    columns_setup = [
        {
            'name':        "NautilusPython::nec_title_column",
            'attribute':   "title",
            'label':       "Title",
            'description': "Song title",
        },
        {
            'name':        "NautilusPython::nec_album_column",
            'attribute':   "album",
            'label':       "Album",
            'description': "Album name",
        },
        {
            'name':        "NautilusPython::nec_artist_column",
            'attribute':   "artist",
            'label':       "Artist",
            'description': "Artist",
        },
        {
            'name':        "NautilusPython::nec_tracknumber_column",
            'attribute':   "tracknumber",
            'label':       "Track",
            'description': "Track number",
        },
        {
            'name':        "NautilusPython::nec_genre_column",
            'attribute':   "genre",
            'label':       "Genre",
            'description': "Genre",
        },
        {
            'name':        "NautilusPython::nec_date_column",
            'attribute':   "date",
            'label':       "Date",
            'description': "Date",
        },
        {
            'name':        "NautilusPython::nec_bitrate_column",
            'attribute':   "bitrate",
            'label':       "Bitrate",
            'description': "Bitrate in kilo bits per second",
        },
        {
            'name':        "NautilusPython::nec_samplerate_column",
            'attribute':   "samplerate",
            'label':       "Sample Rate",
            'description': "Audio sample rate in Hz",
        },
        {
            'name':        "NautilusPython::nec_length_column",
            'attribute':   "length",
            'label':       "Length",
            'description': "Length of audio/video",
        },
        {
            'name':        "NautilusPython::nec_pixeldimensions_column",
            'attribute':   "pixeldimensions",
            'label':       "Image Size",
            'description': "Image/video size - actual pixel dimensions",
        },
        {
            'name':        "NautilusPython::nec_framerate_column",
            'attribute':   "framerate",
            'label':       "FPS",
            'description': "Video frames per second",
        },
        {
            'name':        "NautilusPython::nec_format_column",
            'attribute':   "format",
            'label':       "Format",
            'description': "Multimedia format",
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
                description=col['description'],
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
            MapMediaInfo(filename).to(
                lambda k, v: file_info.add_string_attribute(k, v)
                )

        except Exception as error:
            print("--- ERROR in {} ---\nfile: {}\nmsg:  {}\n---".format(
                self.nec_name,
                filename,
                str(error)
                ))

        file_info.invalidate_extension_info()

        Nautilus.info_provider_update_complete_invoke(
            closure,
            provider,
            handle,
            Nautilus.OperationResult.COMPLETE,
            )

        return False


class MapMediaInfo:
    def __init__(self, file):
        mediainfo = MediaInfo.parse(file)

        for i in mediainfo.tracks:
            n = "map{}".format(i.track_type)
            if method := getattr(self, n, None):
                method(i)

    def to(self, fun) -> None:
        for (k, v) in self.__dict__.items():
            fun(k, v)

    def mapGeneral(self, i) -> None:
        if v := getattr(i, 'other_duration', None):
            self.length = str(v[4])

        if v := getattr(i, 'title', None):
            self.title = getattr(i, 'title', '')

        if v := getattr(i, 'album', None):
            self.album = v

        if v := getattr(i, 'performer', None):
            self.artist = v
        elif v := getattr(i, 'album_performer', None):
            self.artist = v

        if v := getattr(i, 'track_name_position', None):
            self.tracknumber = v

        if v := getattr(i, 'other_overall_bit_rate', None):
            self.bitrate = str(v[0])

        if v := getattr(i, 'format', None):
            self.format = v

        if v := getattr(i, 'genre', None):
            self.genre = v

    def mapAudio(self, i) -> None:
        if v := getattr(i, 'other_sampling_rate', None):
            self.samplerate = str(v[0])

        # file.add_string_attribute('date',info.userdate)

    def mapImage(self, i) -> None:
        if (w := getattr(i, 'height', None)) and \
           (h := getattr(i, 'width', None)):
            self.pixeldimensions = "{}x{}".format(w, h)

    def mapVideo(self, i) -> None:
        if (h := getattr(i, 'height', None)) and \
           (w := getattr(i, 'width', None)):
            self.pixeldimensions = "{}x{}".format(w, h)

        if v := getattr(i, 'frame_rate', None):
            self.framerate = str(v)
