from requests import get
import json
import fnmatch
import os
import errno
import datetime

filepath_pattern = "*ilePat*"
MasterJson_url = 'Master2.json'

def get_inner_fps(fp, dest):
    file_paths_inner = []
    req = make_request(dest, fp)
    m_json = json.loads(req.content.decode('UTF-8'))
    for major_key in m_json.keys():
        for i in m_json[major_key]:
            for x in i.keys():
                if fnmatch.fnmatch(x, filepath_pattern):
                    file_paths_inner.append(i[x])
    return file_paths_inner


def _get_filepaths(master, dest):
    print('begin master', datetime.datetime.now())
    file_paths = []
    m_json = json.loads(master)
    for major_key in m_json.keys():
        if major_key == 'MasterJSON':
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
    print('begin inner', datetime.datetime.now())
    for file in file_paths:
        if '.json' in file:
            inner_paths = get_inner_fps(file, dest)
            if not inner_paths:
                continue
            else:
                for path in inner_paths:
                    file_paths.append(path)

    return file_paths


def get_mjson(dest):
    init_request = make_request(dest, MasterJson_url)
    save_request_content(init_request, MasterJson_url, dest)
    return init_request.content.decode('UTF-8')


def save_request_content(req, p, dest):
    fp = os.path.join("tmp\\{}".format(dest), p)
    if not os.path.exists(os.path.dirname(fp)):
        try:
            os.makedirs(os.path.dirname(fp))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    if not isinstance(req, bytes):
        req.raw.decode_content = True
        with open(fp, "wb") as f:
            f.write(req.content)
    else:
        with open(fp, "wb") as f:
            f.write(req)
    return fp


def make_request(dest, p):
    req = get('https://konfigurace.homecredit.cz/ma/{}/prod/{}'.format(dest.lower(), p), stream=True, verify=False)
    return req


def json_content(p):
    with open(p, "rb") as f:
        return f.read()


def get_files(dest):
    print('getting filepaths', datetime.datetime.now())
    paths_js = dedup_list(_get_filepaths(get_mjson(dest), dest))
    print('started with downloading', datetime.datetime.now())
    for p in paths_js:
        req = make_request(dest, p)
        if req.status_code == 200:
            save_request_content(req, p, dest)
        else:
            print(req.status_code, p)
            continue
    print('end', datetime.datetime.now())


def dedup_list(p_list):
    print('duplication starts', datetime.datetime.now())
    new_list = list(dict.fromkeys(p_list))
    print('duplication ends', datetime.datetime.now())
    return new_list


def check_version(vers, dest):
    date_vers = check_time(vers)
    if date_vers:
        mjson = json.loads(get_mjson(dest))
        version = 0.0
        for i in mjson.keys():
            for main_key in mjson[i]:
                for first_level in mjson[i][main_key]:
                    for f in first_level:
                        if f == 'version':
                            if first_level[f] > version:
                                version = first_level[f]
                        else:
                            if isinstance(first_level[f], list):
                                for second_level in first_level[f]:
                                    for s in second_level.keys():
                                        if s == 'version':
                                            if second_level[s] > version:
                                                version = second_level[s]
        if version < float(vers):
            return True, version
        else:
            return False, version
    else:
        return False, 'yet'


def check_time(vers):
    now = datetime.datetime.now()
    yr = now.year - 2000
    date_now = str(yr)+now.strftime('%m%d')
    date_from_version = str(vers).split('.')[1]
    if date_now >= date_from_version:
        return True
    else:
        return False

check_time('2.200330')