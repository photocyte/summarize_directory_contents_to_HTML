# summarize_directory_contents_to_HTML
A python program with outputs &amp; opens an HTML table summarizing the files in a directory

'''
usage: sum_dir_to_HTML.py [-h] [--filter] [--hash] [--in_dir] DIRECTORY_PATH

This program makes an HTML table summary of a given directory, and opens it in
your default web browser (can be copy pasted into OneNote, EndNote, etc.)

positional arguments:
  DIRECTORY_PATH  The path to the directory to summarize

optional arguments:
  -h, --help      show this help message and exit
  --filter        Filter the results to just .mzML and .d files
  --hash          Calculate the md5sum for files, and the combined recursive
                  md5sum for directories
  --in_dir        Output the resulting HTML file into the directory being
                  summarized (needs write access)
'''
