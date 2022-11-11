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

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "update-documentation"
  cancel-in-progress: true

jobs:
  generate-documentation:
    name: Generate documentation for release
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Generate documentation
        uses: ponylang/library-documentation-action@via-github-action
        with:
          site_url: "https://MYORG.github.io/MYLIBRARY/"
          library_name: "MYLIBRARY"
          docs_build_dir: "build/MY-LIBRARY-docs"
      - name: Setup Pages
        uses: actions/configure-pages@v2
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: 'build/MY-LIBRARY-docs/site/'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v1
```

## Manually triggering a documentation build and deploy

GitHub has a [`workflow_dispatch`](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#workflow_dispatch) event that provides a button the actions UI to trigger the workflow. You can set up a workflow to respond to a workflow_dispatch if you need to regenerate documentation from the last commit on a given branch without doing a full release.

We suggest that you install the a `workflow_dispatch` driven workflow to generate documentation the when you first install this action so you don't need to do a superfluous release.

```yml
name: Manually generate documentation

on:
  workflow_dispatch

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "update-documentation"
  cancel-in-progress: true

jobs:
  generate-documentation:
    name: Generate documentation for release
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Generate documentation
        uses: ponylang/library-documentation-action@via-github-action
        with:
          site_url: "https://MYORG.github.io/MYLIBRARY/"
          library_name: "MYLIBRARY"
          docs_build_dir: "build/MY-LIBRARY-docs"
      - name: Setup Pages
        uses: actions/configure-pages@v2
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1
        with:
          path: 'build/MY-LIBRARY-docs/site/'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v1
```

## Versioning

We used to do versioning for the library-documentation-action but this lead to a lot of extra work each time a new version of ponyc was released. This action is considered feature complete and we don't intend to do any breaking updates to it. It will be deprecated in the future and replaced by a pony documentation command that ships with ponyc.

Until then, to use this action, you should be tracking the `release` docker image and keeping your library up-to-date with any breaking ponyc changes. Using this action without keeping up with changes in ponyc will result in the action failing because the ponyc in the action image is incompatible with your code.
