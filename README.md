# library-documentation-action

A GitHub Action that generates documentation for a Pony library and updates that documentation on GitHub pages. The library in question must have a Makefile with a target `docs` that can be used to generate the documentation that can be feed to `mkdocs`.

Generated docs are uploaded to the branch `generated-documentation` in the repo that this action is installed. Once you have run the action for the first time, you can turn on GitHub Pages for your repository with `generated-documentation` as the branch to build from. After turning on GitHub pages, your new documentation site should be available within a couple minutes.

You need to supply the url of your site to the action in the `site_url` option. For GitHub pages, that domain will be `https://USER_OR_ORG_NAME.github.io/REPOSITORY_NAME/`.

## Example workflow

In **release.yaml**, in addition the usual [release-bot-action](https://github.com/ponylang/release-bot-action) workflow entries.

```yml
name: Release

on:
  push:
    tags:
      - \d+.\d+.\d+

jobs:
  generate-documentation:
    name: Generate documentation for release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v1
      - name: Generate documentation and upload
        uses: ponylang/library-documentation-action@0.1.1
        with:
          site_url: "https://MYORG.github.io/MYLIBRARY/"
          library_name: "MYLIBRARY"
          docs_build_dir: "build/MY-LIBRARY-docs"
          git_user_name: "Ponylang Main Bot"
          git_user_email: "ponylang.main@gmail.com"
        env:
          RELEASE_TOKEN: ${{ secrets.RELEASE_TOKEN }}
```

N.B. The environment variable RELEASE_TOKEN that is required by each step must be a personal access token with public_repo access. You can not use the GITHUB_TOKEN environment variable provided by GitHub's action environment. If you try to use GITHUB_TOKEN, the action will fail when trying to upload the built documentation.

## Manually triggering a documentation build and deploy

GitHub has a [`workflow_dispatch`](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#workflow_dispatch) event that provides a button the actions UI to trigger the workflow. You can set up a workflow to respond to a workflow_dispatch if you need to regenerate documentation from the last commit on a given branch without doing a full release.

We suggest that you install the a `workflow_dispatch` driven workflow to generate documentation the when you first install this action so you don't need to do a superfluous release.

```yml
name: Manually generate documentation

on:
  workflow_dispatch:
    inputs:
      library_name:
        description: 'Name of the library being uploaded'
        required: true
      docs_build_dir:
        description: 'Location, relative to the Makefile, that generated documentation will be placed'
        required: true
      site_url:
        description: 'Url for the site that the documentation will be hosted on'
        required: true
      git_user_name:
        description: 'Name to associate with documentation commits'
        required: true
      git_user_email:
        description: 'Email to associate with documentation commits'
        required: true

jobs:
  generate-documentation:
    name: Generate documentation for release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v1
      - name: Generate documentation and upload
        uses: ponylang/library-documentation-action@0.1.1
        with:
          site_url: ${{ github.event.inputs.site_url }}
          library_name: ${{ github.event.inputs.library_name }}
          docs_build_dir: ${{ github.event.inputs.docs_build_dir }}
          git_user_name: ${{ github.event.inputs.git_user_name }}
          git_user_email: ${{ github.event.inputs.git_user_email }}
        env:
          RELEASE_TOKEN: ${{ secrets.RELEASE_TOKEN }}
```
