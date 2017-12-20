# -*- coding: utf-8 -*-

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

import hashlib
import urllib2
import shutil
import os

import json
from caliper.client.shared import caliper_path
import caliper.server.utils as server_utils
import itertools
import mimetools
import mimetypes
from cStringIO import StringIO
import subprocess
from caliper.server.shared.caliper_path import folder_ope as Folder

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields
        parts.extend(
            [part_boundary,
             'Content-Disposition: form-data; name="%s"' % name,
             '',
             value,
             ]
            for name, value in self.form_fields
        )

        # Add the files to upload
        parts.extend(
            [part_boundary,
             'Content-Disposition: file; name="%s"; filename="%s"' % \
             (field_name, filename),
             'Content-Type: %s' % content_type,
             '',
             body,
             ]
            for field_name, filename, content_type, body in self.files
        )

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)

def upload_result(target,server_url, server_user, server_password):
    '''
    upload result to server
    :param target: target machine running test
    :return: None
    '''
    # get test device config
    get_test_config()
    #workspace dir path for the test, for example: /home/fanxh/caliper_output/hansanyang-OptiPlex-3020_WS_17-05-03_11-29-29
    dirpath = caliper_path.WORKSPACE

    #dir path for score, for example: /home/fanxh/caliper_output/frontend/frontend/data_files/Normalised_Logs
    dir_score_path = caliper_path.HTML_DATA_DIR_OUTPUT

    target_name = server_utils.get_host_name(target)
    #score json file name , for example:hansanyang-OptiPlex-3020_score_post.json
    score_json_file_name = target_name + '_score_post.json'

    #for example, /home/fanxh/caliper_output/frontend/frontend/data_files/Normalised_Logs/hansanyang-OptiPlex-3020_score_post.json
    score_json_file_fullname = os.path.join(dir_score_path,score_json_file_name)

    upload_and_savedb(dirpath,score_json_file_fullname,server_url, server_user, server_password)


def upload_and_savedb(dirpath,json_path_source,server_url, server_user, server_password):
    # tar file
    bin_file = os.path.exists(os.path.join(dirpath,"binary"))
    if bin_file:
        shutil.rmtree(os.path.join(dirpath,"binary"))
    json_file = os.path.join(dirpath,"output", "results", "json")
    json_path=os.path.join(dirpath,os.path.basename(json_path_source))
    shutil.copyfile(json_path_source,json_path)
    output_file=dirpath+".zip"
    json_output_file = dirpath+"_josn.zip"

    encryption(json_file, json_output_file, server_password)
    # # remove json dir
    shutil.rmtree(json_file)
    encryption(dirpath, output_file, server_password)
    hash_output = calcHash(output_file)
    hash_log = calcHash(json_output_file)


    form = MultiPartForm()
    form.add_field('username', server_user)
    json_data = open(json_path, 'r')
    json_data = json_data.read()
    form.add_field('result', json.dumps(json_data))
    form.add_field('hash_output', hash_output)
    form.add_field('hash_log', hash_log)

    # Add a fake file
    form.add_file('output', output_file,
                  fileHandle=StringIO('output'))
    form.add_file('log', json_output_file,
                  fileHandle=StringIO('log'))

    # Build the request
    print 'http://%s/data/upload'%server_url
    request = urllib2.Request('http://%s/data/upload'%server_url)
    body = str(form)
    request.add_header('Content-type', form.get_content_type())
    request.add_header('Content-length', len(body))
    request.add_data(body)

    print
    print 'OUTGOING DATA:'
    print request.get_data()

    print
    print 'SERVER RESPONSE:'
    print urllib2.urlopen(request).read()

def calcHash(filepath):
    '''
    计算文件的hash 值
    :param filepath:
    :return:
    '''
    with open(filepath, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        hash = sha1obj.hexdigest()
    return hash

def encryption(inputpath, outpath, password):
    import subprocess
    subprocess.call("cd %s/.. && zip -rP %s %s %s"%(inputpath, password, outpath, inputpath.split(os.sep)[-1]), shell=True)  # 加密包

def get_test_config():
    sh_path = os.path.join(os.environ['HOME'], '.caliper')
    os.chdir(sh_path)
    subprocess.call('./config_info_run.sh', stdout=subprocess.PIPE, shell=True)
    shutil.copy('/tmp/config_output.json', os.path.join(Folder.json_dir, 'config_output.json'))


# example
#dirpath = "C:\\Users\\yangtt\\Desktop\\fanxh-OptiPlex-3020_WS_17-08-07_11-03-46"
# dirpath = caliper_path.workspace;
#json_path_source="C:\\Users\\yangtt\\Desktop\\Normalised_Logs\\ts-OptiPlex-3020_score_post.json"
# json_path_source = caliper_path.HTML_DATA_DIR_OUTPUT
# upload_and_savedb(dirpath,json_path_source)
