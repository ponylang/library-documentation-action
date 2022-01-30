#!/usr/bin/python3
# pylint: disable=C0103
# pylint: disable=C0114

import json
import os
import os.path
import shutil
import sys
from contextlib import contextmanager
from tempfile import NamedTemporaryFile, mkstemp
from git.exc import GitCommandError

import git
import in_place
import yaml

# Output strings for coloring

ENDC = '\033[0m'
ERROR = '\033[31m'
INFO = '\033[34m'
NOTICE = '\033[33m'

if 'DEPLOY_KEY' in os.environ:
    deploy_key = os.environ['DEPLOY_KEY']
    token = None
elif 'RELEASE_TOKEN' in os.environ:
    deploy_key = None
    token = os.environ['RELEASE_TOKEN']
else:
    print(ERROR + "Either RELEASE_TOKEN or DEPLOY_KEY needs to be set in env. "
          + "Exiting." + ENDC)
    sys.exit(1)

library_name = os.environ['INPUT_LIBRARY_NAME']
docs_build_dir = os.environ['INPUT_DOCS_BUILD_DIR']

#
# make the documentation
#

print(INFO + "Running 'make docs'." + ENDC)
rslt = os.system('make docs')
if rslt != 0:
    print(ERROR + "'make docs' failed." + ENDC)
    sys.exit(1)

mkdocs_yml_file = os.path.join(docs_build_dir, 'mkdocs.yml')
docs_dir = os.path.join(docs_build_dir, 'docs')
index_file = os.path.join(docs_dir, 'index.md')
source_dir = os.path.join(docs_dir, 'src')

#
# remove any docs that aren't part of this library
# store information about removed entries so we can fix up links to them later
#

print(INFO + "Removing 'other docs'." + ENDC)
removed_docs = []
for f in os.listdir(docs_dir):
    if f in ('src', 'index.md'):
        continue

    if not f.startswith(library_name + '-'):
        p = os.path.join(docs_dir, f)
        if os.path.isfile(p):
            os.remove(p)
        else:
            shutil.rmtree(p)
        removed_docs.append(f)

#
# remove any source code that isn't part of this library
#

print(INFO + "Removing 'other sources'." + ENDC)
for f in os.listdir(source_dir):
    if f != library_name:
        p = os.path.join(source_dir, f)
        if os.path.isfile(p):
            os.remove(p)
        else:
            shutil.rmtree(p)

#
# - trim mkdocs.yml down to entries for our library
#   record those packages for later reference
#

print(INFO + "Trimming mkdocs.yml." + ENDC)
mkdocs_yml = {}
packages = []
with open(mkdocs_yml_file, encoding="utf8") as infile:
    mkdocs_yml = yaml.load(infile, Loader=yaml.FullLoader)
    nav = mkdocs_yml['nav']

    new_nav = []
    library_package_key = 'package ' + library_name
    library_subpackage_key = 'package ' + library_name + '/'
    for entry in nav:
        # there's only 1 entry but we don't know what it is because
        # well that's how the yaml package represents this thing should be a
        # 2-element tuple or list
        for k in entry.keys():
            if k == library_name:
                # library index entry. keep it.
                new_nav.append(entry)

            if k == library_package_key \
              or k.startswith(library_subpackage_key):
                # package entry. keep it.
                # record the package name for later usage
                new_nav.append(entry)
                # entry will look like one of:
                # package semver
                # package semver/subpackage
                packages.append(k[8:])

    mkdocs_yml['nav'] = new_nav

# add a site url to fix some /asset links
# without this, the 404 page will be broken
mkdocs_yml['site_url'] = os.environ['INPUT_SITE_URL']

with open(mkdocs_yml_file, 'w', encoding="utf8") as outfile:
    yaml.dump(mkdocs_yml, outfile)

#
# trim docs/index.md down to entries for our library
#

print(INFO + "Trimming index.md." + ENDC)
with in_place.InPlace(index_file) as fp:
    for line in fp:
        if not line.startswith('*'):
            fp.write(line)
        else:
            for p in packages:
                if line.startswith('* [' + p + ']'):
                    fp.write(line)

#
# `make docs` at the start will have pulled down any needed dependencies that
# we might have. Here we are going to reach into the _corral directory to find
# the `corral.json` for any dependencies and get:
# - the package names
# - the location of the documentation_url
#
# This should eventually be incorporated into `corral` as a command
# or something similar. In the meantime, we are doing "by hand" in this
# action as we work out how to accomplish everything that we want to.
#
# This could grab info about "extra" packages as there is on guarantee that a
# dependency that was removed isn't still in _corral directory assuming that
# this code was used outside of the context of this action that starts from a
# clean-slate. That's not an edge condition to worry about at this time.
#
# packages provided are listed in `corral.json` in an array with the key
# `packages`. Every package needs to be listed including those that are
# "subpackages" so for example, we have package listings for `semver`,
# `semver/constraint`, and `semver/version`.
#
# The documentation_url for a given package is located in the `info` object
# in the `documentation_url` field.
#

documentation_urls = {}

if os.path.isdir("_corral"):
    dependencies_dirs = os.listdir("_corral")
    for dd in dependencies_dirs:
        corral_file = "/".join(["_corral", dd, "corral.json"])
        if not os.path.isfile(corral_file):
            print(NOTICE + "No corral.json in " + dd + "." + ENDC)
            continue

        with open(corral_file, 'r', encoding="utf8") as corral_file:
            corral_data = json.load(corral_file)
            bundle_documentation_url = ""
            try:
                bundle_documentation_url = corral_data['info']['documentation_url']
            except KeyError as e:
                print(NOTICE + "No documentation_url in " + corral_file + "." \
                  + ENDC)

            try:
                packages = corral_data['packages']
                for p in packages:
                    documentation_urls[p] = bundle_documentation_url
            except KeyError as e:
                print(NOTICE + "No packages in " + corral_file + "." \
                  + ENDC)

#
# Go through the markdown belonging to our package and replace missing entries
# with links to their external sites.
#

print(INFO + "Fixing links to code outside of our package." + ENDC)
for f in os.listdir(docs_dir):
    if f == "src":
        continue

    p = os.path.join(docs_dir, f)
    print(INFO + "Fixing links in " + str(p) + "." + ENDC)
    with in_place.InPlace(p) as fp:
        for line in fp:
            for removed in removed_docs:
                if removed in line:
                    print(INFO + "Replacing link for " + removed + "." + ENDC)

                    # get the package name
                    s = removed.replace('.md', '')
                    s = s.split('-')
                    if len(s) > 1:
                        del s[-1]
                    package_name = '/'.join(s)

                    # if unknown package, we'll use the standard library
                    external_url = documentation_urls.get(package_name, \
                      'https://stdlib.ponylang.io/')

                    # as the external url is input from users, it might not
                    # include a trailing slash. if not, generated urls will
                    # be broken.
                    # there's far more validation we could do here, but in
                    # terms of helping out a non-malicious user, this is the
                    # minimum
                    if not external_url.endswith('/'):
                        external_url += '/'

                    as_html = removed.replace('.md', '')
                    link = external_url + as_html + "/"
                    line = line.replace(removed, link)

            fp.write(line)

#
# run mkdocs to actually build the content
#

print(INFO + "Setting up git configuration." + ENDC)
git = git.Repo().git
git.config('--global', 'user.name', os.environ['INPUT_GIT_USER_NAME'])
git.config('--global', 'user.email', os.environ['INPUT_GIT_USER_EMAIL'])
if deploy_key:
    @contextmanager
    def git_auth():
        """
        Temporarily set SSH credentials for Git. To be used as context manager.
        """
        (ssh_wrapper_fd, ssh_wrapper_path) = mkstemp(text=True)
        try:
            with NamedTemporaryFile() as identity_file:
                with open(ssh_wrapper_fd, "w", encoding="utf8") as ssh_wrapper_file:
                    ssh_wrapper_file.write('#!/bin/sh\n')
                    ssh_wrapper_file.write(
                        f'exec ssh -o StrictHostKeyChecking=no '
                        f'-i {identity_file.name} $@')
                    os.chmod(ssh_wrapper_path, 0o500)

                identity_file.write(deploy_key.encode('utf-8'))
                if not deploy_key.endswith("\n"):
                    identity_file.write("\n")
                identity_file.flush()
                os.environ['GIT_SSH'] = ssh_wrapper_path
                try:
                    yield
                finally:
                    del os.environ['GIT_SSH']
        finally:
            os.unlink(ssh_wrapper_path)

    remote = f'git@github.com:{os.environ["GITHUB_REPOSITORY"]}'
else:
    @contextmanager
    def git_auth():
        """
        No-op context manager.
        """
        yield

    remote = f'https://{token}@github.com/{os.environ["GITHUB_REPOSITORY"]}'
git.remote('add', 'gh-token', remote)
with git_auth():
    git.fetch('gh-token')
    # reset will fail if 'generated-documentation` branch doesn't yet exist.
    # That's fine, it will exist after our push. Just not the error and move on.
    try:
        git.reset('gh-token/generated-documentation')
    except GitCommandError:
        print(NOTICE + "Couldn't git reset generated-documentation." + ENDC)
        print(NOTICE + "This error is expected if the branch doesn't exist yet."
          + ENDC)

    print(INFO + "Running 'mkdocs gh-deploy'." + ENDC)
    os.chdir(docs_build_dir)
    rslt = os.system(
        'mkdocs gh-deploy --verbose --clean --remote-name gh-token '
        '--remote-branch generated-documentation')
if rslt != 0:
    print(ERROR + "'mkdocs gh-deploy' failed." + ENDC)
    sys.exit(1)
