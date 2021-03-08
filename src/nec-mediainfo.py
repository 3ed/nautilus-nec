#!/usr/bin/python
import gi
from gi.repository import Nautilus, GObject
from urllib.parse import unquote as uri_unescape
from pymediainfo import MediaInfo

gi.require_version('Nautilus', '3.0')


class NecMediainfo(GObject.GObject,
                   Nautilus.ColumnProvider,
                   Nautilus.InfoProvider, ):

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
        print("* Starting nec-mediainfo.py")
        pass

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

        if file_info.get_uri_scheme() == 'file' \
           and file_info.get_mime_type() in self.mime_do:
            filename = uri_unescape(file_info.get_uri()[7:])

            GObject.idle_add(
                self.do_mediainfo,
                provider,
                handle,
                closure,
                file_info,
                filename,
                )

            return Nautilus.OperationResult.IN_PROGRESS

        return Nautilus.OperationResult.COMPLETE

    def do_mediainfo(self, provider, handle, closure, file_info, filename):
        try:
            mi = MediaInfo.parse(filename)

            for i in mi.tracks:
                if 'General' == i.track_type:
                    self.do_map_mediainfo_general(file_info, i)

                elif 'Audio' == i.track_type:
                    self.do_map_mediainfo_audio(file_info, i)

                elif 'Image' == i.track_type:
                    self.do_map_mediainfo_image(file_info, i)

                elif 'Video' == i.track_type:
                    self.do_map_mediainfo_video(file_info, i)

        except Exception:
            print("{}: nec-mediainfo bailout here (skipping)".format(filename))
            # return

        file_info.invalidate_extension_info()

        Nautilus.info_provider_update_complete_invoke(
            closure, provider, handle, Nautilus.OperationResult.COMPLETE,
            )

        return False

    def do_map_mediainfo_general(self, file_info, i):
        if i.other_duration is not None:
            v = str(i.other_duration[4])
            file_info.add_string_attribute('length', v)

        if i.title is not None:
            v = i.title
            file_info.add_string_attribute('title', v)

        if i.album is not None:
            v = i.album
            file_info.add_string_attribute('album', v)

        if i.album_performer is not None:
            v = i.album_performer
            file_info.add_string_attribute('artist', v)

        if i.performer is not None:
            v = i.performer
            file_info.add_string_attribute('artist', v)

        if i.track_name_position is not None:
            v = i.track_name_position
            file_info.add_string_attribute('tracknumber', v)

        if i.other_overall_bit_rate is not None:
            v = str(i.other_overall_bit_rate[0])
            file_info.add_string_attribute('bitrate', v)

        if i.format is not None:
            v = i.format
            file_info.add_string_attribute('format', v)

        if i.genre is not None:
            v = i.genre
            file_info.add_string_attribute('genre', v)

    def do_map_mediainfo_audio(self, file_info, i):
        if i.other_sampling_rate is not None:
            v = str(i.other_sampling_rate[0])
            file_info.add_string_attribute('samplerate', v)

        # file.add_string_attribute('date',info.userdate)

    def do_map_mediainfo_image(self, file_info, i):
        if i.height is not None and i.width is not None:
            v = "{}x{}".format(i.width, i.height)
            file_info.add_string_attribute('pixeldimensions', v)

    def do_map_mediainfo_video(self, file_info, i):
        if i.height is not None and i.width is not None:
            v = "{}x{}".format(i.width, i.height)
            file_info.add_string_attribute('pixeldimensions', v)

        if i.frame_rate is not None:
            v = str(i.frame_rate)
            file_info.add_string_attribute('framerate', v)
