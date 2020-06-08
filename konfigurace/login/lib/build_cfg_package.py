from requests import get
import json
import fnmatch
import os
import errno
import datetime
import urllib3
from git import Repo

#git config --global http.sslVerify false

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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


def get_mjson(dest, version):
    init_request = make_request(dest, MasterJson_url)
    save_request_content(init_request, MasterJson_url, dest, version)
    return init_request.content.decode('UTF-8')


def save_request_content(req, p, dest, version):
    fp = os.path.join("tmp/{}/{}".format(dest, version), p)
    if not os.path.exists(os.path.dirname(fp)):
        try:
            os.makedirs(os.path.dirname(fp))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    if not isinstance(req, bytes) and not isinstance(req, dict):
        req.raw.decode_content = True
        with open(fp, "wb") as f:
            f.write(req.content)
    elif isinstance(req, bytes):
        with open(fp, "wb") as f:
            f.write(req)
    elif isinstance(req, dict):
        with open(fp, "w+", encoding='UTF-8') as f:
            json.dump(req, f, indent=4, sort_keys=False, ensure_ascii=False)
    return fp


def make_request(dest, p):
    req = get('https://konfigurace.homecredit.cz/ma/{}/prod/{}'.format(dest.lower(), p), stream=True, verify=False)
    return req


def json_content(dest, version):
    with open('tmp/{}/{}/{}'.format(dest, version, MasterJson_url), "rt", encoding='UTF-8') as f:
        return json.loads(f.read())


def get_files(dest, version):
    print('getting filepaths', datetime.datetime.now())
    paths_js = dedup_list(_get_filepaths(get_mjson(dest, version), dest))
    print('started with downloading', datetime.datetime.now())
    for p in paths_js:
        req = make_request(dest, p)
        if req.status_code == 200:
            save_request_content(req, p, dest, version)
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
        mjson = json.loads(get_mjson(dest, vers))
        version = 0.0
        for i in mjson.keys():
            for main_key in mjson[i]:
                for first_level in mjson[i][main_key]:
                    for f in first_level:
                        if f == 'version' and first_level[f] > version:
                            version = first_level[f]
                        else:
                            if isinstance(first_level[f], list):
                                for second_level in first_level[f]:
                                    for s in second_level.keys():
                                        if s == 'version' and second_level[s] > version:
                                            version = second_level[s]
        if version < float(vers):
                return True, version
        else:
            return False, version
    else:
        return False, 'yet'


def get_version(dest, settings, new_version):
    mjson = json_content(dest, new_version)
    primary_dicts = mjson['MasterJSON'][settings]
    version_list = []
    if isinstance(primary_dicts, list):
        for i in primary_dicts:
            for ik in i.keys():
                if ik != 'version' and isinstance(i[ik], list):
                    for ikx in i[ik]:
                        for ikxk in ikx.keys():
                            if ikxk == 'version':
                                version_list.append(ikx[ikxk])
                elif ik == 'version':
                    version = i[ik]
                    version_list.append(version)
    return version_list


def change_decision(dest, case, new_version):

    if case.lower() == 'loyalty' and new_version:
        settings = 'unpersonifiedOfferSettings'
        old_version = get_version(dest, settings, new_version)
        change_version(dest, settings, old_version, new_version)

    elif case.lower() == 'banners_android' and new_version:
        settings = "bannersSettings\""
        old_settings = "bannersSettings"
        to_version = "bannersSettings_iOS"
        old_version = get_version(dest, old_settings, new_version)
        change_version(dest, settings, old_version, new_version, to_version)

    elif case.lower() == 'banners_ios' and new_version:
        settings = "bannersSettings_iOS\""
        old_settings = "bannersSettings_iOS"
        to_version = "cardSettings"
        old_version = get_version(dest, old_settings, new_version)
        print(old_version)
        change_version(dest, settings, old_version, new_version, to_version)


def change_version(dest, settings, version, new_version, to_version=None):

    if settings == "unpersonifiedOfferSettings":

        if version[1] == '' or version[0] == version[1]:
            with open('tmp/{}/{}/{}'.format(dest, new_version, MasterJson_url), 'rt', encoding='utf-8') as lolc:
                lolss = lolc.read().split(settings)

            with open('tmp/{}/{}/{}'.format(dest, new_version, MasterJson_url), 'wt', encoding='utf-8') as lolg:
                lxs = lolss[1].replace(str(version[0]), str(new_version))
                lolg.write(lolss[0] + settings + lxs)
    else:
        with open('tmp/{}/{}/{}'.format(dest, new_version, MasterJson_url), 'rt', encoding='utf-8') as lolc:
            lolss = lolc.read().split(settings)
            get_android_part = lolss[1].split(to_version)

        with open('tmp/{}/{}/{}'.format(dest, new_version, MasterJson_url), 'wt', encoding='utf-8') as lolg:
            lxs = get_android_part[0].replace(str(version[0]), str(new_version))
            lolg.write(lolss[0] + settings + lxs + to_version + get_android_part[1])



def check_time(vers):
    now = datetime.datetime.now()
    yr = now.year - 2000
    date_now = str(yr)+now.strftime('%m%d')
    date_from_version = str(vers).split('.')[1]
    if date_now >= date_from_version:
        return True
    else:
        return False


def git_push(version, country):
    repo = Repo('tmp')
    if country.upper() == 'CZ':
        repo.index.add(['CZ'])
    elif country.upper() == 'SK':
        repo.index.add(['SK'])

    with repo.git.custom_environment(GIT_SSH_COMMAND='ssh -v -i /home/azureuser/.ssh/omg'):
        repo.index.commit(version)
        origin = repo.remote('origin')
        origin.push()
    return "https://github.com/koubicl/configs/tree/master/{}/{}".format(country.upper(), version)
