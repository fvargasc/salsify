import os
import time
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())

INPUT_FILES_DIRECTORY = os.environ.get('INPUT_FILES_DIRECTORY')  # Directory where text files will be placed
TEXT_FILENAME = "%s/%s" % (INPUT_FILES_DIRECTORY, os.environ.get('TEXT_FILENAME'))  # Name of the file containing the source text

IDX_FILENAME = "%s.idx" % TEXT_FILENAME  # Name of the file with the lines index
IDX_TMP_FILENAME = "%s.tmp" % IDX_FILENAME  # Name of temp file used during index generation

IDX_ENTRY_LENGTH_BYTES = 8  # Let's use 64 bit integer values for the index entries
IDX_ENTRY_BYTE_ENDIAN = 'big'  # using big endian (MSB comes first)


# Gets the text from a line identified by its index
def get_line_text(line_index):
    # check if entry exists in the index
    if os.path.getsize(IDX_FILENAME) / IDX_ENTRY_LENGTH_BYTES <= line_index:
        raise LineDoesNotExistException()

    # open index for reading
    with open(IDX_FILENAME, 'rb') as idx_file:
        # move file cursor to specified index entry
        idx_file.seek(line_index * IDX_ENTRY_LENGTH_BYTES)

        # read indexed line position from index file
        line_position = from_bytes(
            idx_file.read(IDX_ENTRY_LENGTH_BYTES))

        # open source-text file for reading, and read line from the indexed position
        with open(TEXT_FILENAME, 'r') as text_file:
            text_file.seek(line_position)
            line_text = text_file.readline()

    return line_text


def do_preprocess_checks():
    if not TEXT_FILENAME:
        LOGGER.error("Target file name was not specified.")
        raise ValueError

    if not os.path.exists(TEXT_FILENAME):
        LOGGER.error("File %s does not exist." % TEXT_FILENAME)
        raise FileNotFoundError

    return


# Runs the indexing for the source text file
def preprocess_file():
    do_preprocess_checks()

    if os.path.exists(IDX_FILENAME):
        LOGGER.info("Reusing existing index file %s" % IDX_FILENAME)
        return

    text_file_size = os.path.getsize(TEXT_FILENAME)

    LOGGER.info("Pre-processing file (%dMB)..." % (text_file_size >> 20))
    ts_start = time.time()

    cursor_position = 0

    # open files for indexing
    with open(TEXT_FILENAME, 'r') as text_file:

        with open(IDX_TMP_FILENAME, 'wb') as fw:
            fw.seek(IDX_ENTRY_LENGTH_BYTES)

            for line in text_file:
                cursor_position += len(line)
                fw.write(to_bytes(cursor_position))

                if cursor_position % 100000 == 0: # ballpark value
                    LOGGER.info("%d%%" % (cursor_position * 100 / text_file_size))

    # rename temp index file to its final name
    os.rename(IDX_TMP_FILENAME, IDX_FILENAME)

    LOGGER.info("Finished. Took %.2f seconds" %
                (time.time() - ts_start))
    LOGGER.info("Text size: %dMB       Index size: %dMB" % (
        text_file_size >> 20,
        os.path.getsize(IDX_FILENAME) >> 20))

    return


# Define a new Exception class to be raised  when a specified line does not exist.
class LineDoesNotExistException(Exception):
    pass


# Simple utility function to convert int values to a application-specific byte representation
def to_bytes(int_value):
    return int_value.to_bytes(IDX_ENTRY_LENGTH_BYTES, IDX_ENTRY_BYTE_ENDIAN)


# Converts bytes to int values, using the application-specific byte representation
def from_bytes(byte_value):
    return int.from_bytes(byte_value, IDX_ENTRY_BYTE_ENDIAN)


def main():
    try:
        preprocess_file()
    except (FileNotFoundError, ValueError):
        exit(1)


# Main routine is run when this script is executed directly
if __name__ == '__main__':
    main()
