import getopt
import sys
from os import listdir, mkdir, rename
from os.path import isfile, join, isdir
from datetime import datetime
import struct

from PIL import Image, ExifTags

date_time_format = '%Y:%m:%d %H:%M:%S'


def get_source_destination():
    source_path = None
    destination_path = None

    opts, args = getopt.getopt(sys.argv[1:], "s:d:")
    for opt in opts:
        if opt[0] == '-s':
            source_path = opt[1]
        if opt[0] == '-d':
            destination_path = opt[1]

    return source_path, destination_path


def get_source_files(source_path):
    return [f for f in listdir(source_path) if can_import(join(source_path, f))]


def can_import(file):
    return isfile(file) and (
                file.lower().endswith('.jpeg') or file.lower().endswith('.jpg') or file.lower().endswith('.mov'))


def get_datetime(image_path):
    if image_path.lower().endswith('.mov'):
        creation_time, modification_time = get_mov_timestamps(image_path)
        return creation_time
    if image_path.endswith('.jpeg') or image_path.endswith('.jpg'):
        img = Image.open(image_path)
        # noinspection PyProtectedMember
        exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
        date_time_original_str = exif['DateTimeOriginal']
        date_time_original = datetime.strptime(date_time_original_str, date_time_format)
        return date_time_original


def build_destination_dir(destination_path, date_time_original: datetime):
    year_path = join(destination_path, str(date_time_original.year))
    if not isdir(year_path):
        mkdir(year_path)
    month_path = join(destination_path, str(date_time_original.year), "{:02d}".format(date_time_original.month))
    if not isdir(month_path):
        mkdir(month_path)

    return month_path


def move_image(source_path, final_destination, file):
    if not isfile(join(final_destination, file)):
        rename(join(source_path, file), join(final_destination, file))
    else:
        raise FileExistsError(join(final_destination, file))


def get_mov_timestamps(filename):
    """ Get the creation and modification date-time from .mov metadata.

        Returns None if a value is not available.
    """

    atom_header_size = 8
    # difference between Unix epoch and QuickTime epoch, in seconds
    epoch_adjuster = 2082844800

    creation_time = modification_time = None

    # search for moov item
    with open(filename, "rb") as f:
        while True:
            atom_header = f.read(atom_header_size)
            # ~ print('atom header:', atom_header)  # debug purposes
            if atom_header[4:8] == b'moov':
                break  # found
            else:
                atom_size = struct.unpack('>I', atom_header[0:4])[0]
                f.seek(atom_size - 8, 1)

        # found 'moov', look for 'mvhd' and timestamps
        atom_header = f.read(atom_header_size)
        if atom_header[4:8] == b'cmov':
            raise RuntimeError('moov atom is compressed')
        elif atom_header[4:8] != b'mvhd':
            raise RuntimeError('expected to find "mvhd" header.')
        else:
            f.seek(4, 1)
            creation_time = struct.unpack('>I', f.read(4))[0] - epoch_adjuster
            creation_time = datetime.fromtimestamp(creation_time)
            if creation_time.year < 1990:  # invalid or censored data
                creation_time = None

            modification_time = struct.unpack('>I', f.read(4))[0] - epoch_adjuster
            modification_time = datetime.fromtimestamp(modification_time)
            if modification_time.year < 1990:  # invalid or censored data
                modification_time = None

    return creation_time, modification_time
