#!/usr/bin/python3
# pylint: disable=C0103
# pylint: disable=C0114

import os
import shutil
import sys
import git
import in_place
import yaml

# Output strings for coloring

ENDC = '\033[0m'
ERROR = '\033[31m'
INFO = '\033[34m'
NOTICE = '\033[33m'

if 'GITHUB_TOKEN' not in os.environ:
    print(ERROR + "GITHUB_TOKEN needs to be set in env. Exiting." + ENDC)
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
    else:
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
#

print(INFO + "Trimming mkdocs.yml." + ENDC)
mkdocs_yml = {}
with open(mkdocs_yml_file) as infile:
    mkdocs_yml = yaml.load(infile, Loader=yaml.FullLoader)
    nav = mkdocs_yml['nav']

    new_nav = []
    library_package_key = 'package ' + library_name
    for entry in nav:
        print(entry)
        if  library_name in entry or library_package_key in entry:
            # it's part of our package, keep it
            new_nav.append(entry)

    mkdocs_yml['nav'] = new_nav

with open(mkdocs_yml_file, 'w') as outfile:
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
            if line.startswith('*[' + library_name + ']'):
                fp.write(line)

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
                    as_html = removed.replace('.md', '')
                    link = 'https://stdlib.ponylang.io/' + as_html + "/"
                    line = line.replace(removed, link)
        fp.write(line)

#
# run mkdocs to actually build the content
#

print(INFO + "Setting up git configuration." + ENDC)
git = git.Repo().git
git.config('--global', 'user.name', os.environ['INPUT_GIT_USER_NAME'])
git.config('--global', 'user.email', os.environ['INPUT_GIT_USER_EMAIL'])
github_token  = os.environ['GITHUB_TOKEN']
remote = 'https://' + github_token + '@github.com/' + os.environ['GITHUB_REPOSITORY']
git.remote('add', 'gh-token', remote)
git.fetch('gh-token')

os.chdir(docs_build_dir)
rslt = os.system('mkdocs gh-deploy --verbose --clean \
    --remote-name gh-token --remote-branch generated-documentation')
if rslt != 0:
    print(ERROR + "'mkdocs gh-deploy' failed." + ENDC)
    sys.exit(1)
