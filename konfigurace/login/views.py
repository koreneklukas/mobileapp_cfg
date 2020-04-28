from django.shortcuts import render
from .lib.build_cfg_package import get_files, check_version, git_push
from .lib.loyalty_steps import step_one, step_two

# Create your views here.

creds = {'lol': 'lol123'}
variablex = {}


def index(request):
    return render(request, 'home.html')


def login(request):
    username = request.POST['username']
    password = request.POST['pass']
    if username not in creds.keys() or creds[username] != password:
        return render(request, 'home.html', {"result": "Bad password."})
    return render(request, 'set-version.html')


def success(request):
    return render(request, 'rozcestnik-2.html', {'result': 'Everything is ok, configuration is in progress.',
                                               'version': store_version_variable(), 'country': store_country_variable()})


def back_to_tree(request):
    return render(request, 'rozcestnik.html',
                  {'version': store_version_variable(), 'country': store_country_variable()})


def tree(request):
    version_new = {'version': str(request.POST['version'])}
    country_new = {'country': request.POST['country']}
    check, vers = check_version(str(request.POST['version']), request.POST['country'])
    if check:
        store_version_variable(version_new)
        store_country_variable(country_new)
        get_files(store_country_variable(), store_version_variable())
        return render(request, 'rozcestnik.html',
                      {'version': store_version_variable(), 'country': store_country_variable()})
    elif not check and vers == 'yet':
        return render(request, 'set-version.html',
                      {'result': 'You are trying to insert version newer than actual date.'})
    else:
        return render(request, 'set-version.html',
                      {'result': 'There is a newer version on production already. ({})'.format(vers)})


def loyalty(request):
    version = store_version_variable()
    return render(request, 'loyalty_step_1.html', {'version': version, 'country': store_country_variable()})


def git(request):
    version = store_version_variable()
    country = store_country_variable()
    url = git_push(str(version), str(country))
    return render(request, 'rozcestnik-2.html', {'version': version, 'country': store_country_variable(), 'url': url})


def store_version_variable(variable=None):
    if variable:
        variablex.update(variable)
    else:
        return variablex['version']


def store_country_variable(variable=None):
    if variable:
        variablex.update(variable)
    else:
        return variablex['country']


def loyalty_proceed_1_step(request):
    page = 'loyalty_step_1.html'
    result = step_one(request, page, store_version_variable(), store_country_variable())
    return result


def loyalty_proceed_2_step(request):
    page = 'loyalty_step_2.html'
    result = step_two(request, page, store_version_variable(), store_country_variable())
    return result
