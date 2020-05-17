# main-actor-documentation-action

A GitHub Action that generates documentation for a Pony library and updates that documentation to [main.actor](https://main.actor). The library in question must have a Makefile with a target `docs` that can be used to generate the documentation.

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
        uses: ponylang/main-actor-documentation-action@master
        with:
          library_name: "MYLIBRARY"
          docs_build_dir: "docs/build-MYLIBRARY"
          git_user_name: "Ponylang Main Bot"
          git_user_email: "ponylang.main@gmail.com"
        env:
          RELEASE_TOKEN: ${{ secrets.RELEASE_TOKEN }}
```

N.B. The environment variable RELEASE_TOKEN that is required by each step must be a personal access token with at least public_repo access. You can not use the GITHUB_TOKEN environment variable provided by GitHub's action environment. If you try to use GITHUB_TOKEN, the action will fail.

## Additional setup

Any user or organization that intends to use this action must have set up a fork of the [ponylang/main.actor-package-markdown](https://github.com/ponylang/main.actor-package-markdown) repository.

So for example, if your GitHub user name is `JeannieQPublic`, then there needs to be a fork of `main.actor-package-markdown` at `JeannieQPublic/main.actor-package-markdown`.

The personal access token user in the workflow configuration as `RELEASE_TOKEN` must have at least `public_repo` access to the `main.actor-package-markdown` fork.
