#!/usr/bin/env python
# coding: utf-8

import os
import pathlib ##See https://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
import datetime
import humanize
import pandas
import hashlib
import subprocess
from IPython.display import HTML
import tempfile
import webbrowser

import argparse
parser = argparse.ArgumentParser(description='This program makes an HTML table summary of a given directory, and opens it in your default web browser (can be copy pasted into OneNote, EndNote, etc.)')
parser.add_argument("DIRECTORY_PATH",help="The path to the directory to summarize")
parser.add_argument("--filter",default=False,action='store_true',help="Filter the results to just .mzML and .d files")
parser.add_argument("--hash",default=False,action='store_true',help="Calculate the md5sum for files, and the combined recursive md5sum for directories")
parser.add_argument("--in_dir",default=False,action='store_true',help="Output the resulting HTML file into the directory being summarized (needs write access)")
args = parser.parse_args()
parser.parse_args()

doHashSwitch = args.hash
nameFilterSwitch = args.filter
filterList = [".d"]

def md5_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def md5_list(theList):
    hash_md5 = hashlib.md5()
    for chunk in theList:
        hash_md5.update(chunk.encode('utf-8'))
    return hash_md5.hexdigest()

def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))

##From https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
def recursive_directory_analyze(start_path = '.',max_count=100000,doHashes=True):
    total_size = 0
    count = 0
    hashes = []
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            count += 1
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
                if doHashes:
                    hashes.append(md5_file(fp))
            if count > max_count:
                break
    if doHashes:
        overall_hash = md5_list(hashes)
    else:
        overall_hash = "not determined"
    return total_size,count,overall_hash

##From https://stackoverflow.com/questions/38181554/md5sum-shell-script-and-python-hashlib-md5-is-different/38181627

df = pandas.DataFrame(columns = ['Path', 'Type', 'Size', '# entries', 'md5sum',"last modified time",'create time'])

folder = args.DIRECTORY_PATH
filepaths = [os.path.join(folder, f) for f in os.listdir(folder)]
for f in filepaths:
    fpathlib_obj = pathlib.Path(f)
    
    if nameFilterSwitch:
        includeFile = False
        for key in filterList:
            if key in fpathlib_obj.name:
                includeFile = True
        if includeFile == False:
            continue
    
    artifact_type = 'unknown'
    
    mtime = datetime.datetime.fromtimestamp(fpathlib_obj.stat().st_mtime)
    btime = datetime.datetime.fromtimestamp(fpathlib_obj.stat().st_birthtime )
    artifact_modify = mtime
    artifact_birth = btime
    
    if os.path.isfile(f):
        artifact_type = 'file'
    elif os.path.isdir(f):
        artifact_type = 'dir'
    elif os.path.islink(f):
        artifact_type = 'symlink'
    
    artifact_size = -1
    artifact_number = -1
    artifact_hash = "unknown"
    if artifact_type == 'file':
        artifact_size = humanize.naturalsize(os.path.getsize(f))
        artifact_number = 1
        if doHashSwitch:
            artifact_hash = md5_file(f)
        else:
            artifact_hash = "not determined"
    
    if artifact_type == 'dir':
        artifact_size, artifact_number, artifact_hash = recursive_directory_analyze(f,doHashes=doHashSwitch)
        artifact_size =  humanize.naturalsize(artifact_size)
        for c in os.walk(f):
            artifact_number +=1
            #print(c)

    rowDict = {'Path':'<a href="file://'+os.path.abspath(f)+'">'+fpathlib_obj.name+'</a>',               'Type':artifact_type,'Size':artifact_size,               '# entries':artifact_number,               'md5sum':artifact_hash,               'last modified time':artifact_modify,               'create time':artifact_birth}
    ##rowDict = {'Path':'file://'+os.path.abspath(f),'Type':artifact_type,'Size':artifact_size,'# entries':artifact_number,'md5sum':artifact_hash}


    df = df.append(rowDict,ignore_index=True)
df = df.sort_values(by=['Path'],ascending=True)
html_string = df.to_html(escape=False,index=False)
#print(html_string)

##write_to_clipboard(html_string)
##HTML(html_string)

fd, tmpPath = tempfile.mkstemp(suffix=".html")
try:
    with os.fdopen(fd, 'w') as tmp:
        # do stuff with temp file
        tmp.write(html_string)
        print(tmpPath)
        file_location = "file:///" + tmpPath
        webbrowser.get().open(file_location, new=2)
        ##webbrowser.open(tmpPath)
        #process = subprocess.Popen(
        #'open -a "Safari" '.split()+[tmpPath], env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
finally:
    pass





