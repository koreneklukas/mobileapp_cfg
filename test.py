from requests import get
import json
import fnmatch
import os
import errno

filepath_pattern = "*ilePath*"
MasterJson_url = '.\Master2.json'

def make_request(dest, p):
    req = get('https://konfigurace.homecredit.cz/ma/{}/prod/{}'.format(dest.lower(), p), stream=True)
    return req


def json_content(p):
    with open(p, "r") as f:
        return json.loads(f.read())

def get_files(dest):
    paths = dedup_list(_get_filepaths(_get_mjson(dest)))
    for p in paths:
        req = make_request(dest, p)
        if req.status_code == 200:
            fp = save_request_content(req, p, dest)
        else:
            print(req.status_code, p)
            continue
        if '.json' in p:
            content = json_content(fp)
            for key in content.keys():
                if fnmatch.fnmatch(key, filepath_pattern):
                    get_inner_file = make_request(dest, p[key])
                    save_request_content(get_inner_file, p, dest)
                for x in key.keys():
                    if fnmatch.fnmatch(x, filepath_pattern):
                        get_inner_file = make_request(dest, key[x])
                        save_request_content(get_inner_file, p, dest)
                    for y in x.keys():
                        if fnmatch.fnmatch(x, filepath_pattern):
                            get_inner_file = make_request(dest, x[y])
                            save_request_content(get_inner_file, p, dest)
    return file_paths

_get_filepaths()


def _get_filepaths(master):
    file_paths = []
    m_json = json.loads(master)
    for major_key in m_json.keys():
        for i in m_json[major_key].keys():
            for x in m_json[major_key][i]:
                for xs in x.keys():
                    if fnmatch.fnmatch(xs, filepath_pattern):
                        file_paths.append(x[xs])
                    if isinstance(x[xs], list):
                        for c in x[xs]:
                            for cx in c.keys():
                                if fnmatch.fnmatch(cx, filepath_pattern):
                                    file_paths.append(c[cx])
                                if isinstance(c[cx], list):
                                    for d in c[cx]:
                                        for dx in d.keys():
                                            if fnmatch.fnmatch(dx, filepath_pattern):
                                                file_paths.append(d[dx])
    return file_paths