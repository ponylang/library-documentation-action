# library-documentation-action

A GitHub Action that generates documentation for a Pony library and updates that documentation on GitHub pages. The library in question must have a Makefile with a target `docs` that can be used to generate the documentation.

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
        uses: ponylang/library-documentation-action@0.0.0
        with:
          library_name: "MYLIBRARY"
          docs_build_dir: "build/MY-LIBRARY-docs"
          git_user_name: "Ponylang Main Bot"
          git_user_email: "ponylang.main@gmail.com"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
