from os.path import join
from src.utilties.Basics import get_source_destination, get_source_files, get_datetime, build_destination_dir, \
    move_image

source_path, destination_path = get_source_destination()
source_files = get_source_files(source_path)

print(source_path)
print(destination_path)

for file in source_files:
    print('moving file:', file)
    try:
        date_time_original = get_datetime(join(source_path, file))
        if date_time_original is not None:
            final_destination = build_destination_dir(destination_path, date_time_original)
            move_image(source_path, final_destination, file)
    except KeyError:
        print('not moving file: ', file)
    except FileExistsError:
        print('not moving file: ', file)
    except AttributeError:
        print('not moving file: ', file)
