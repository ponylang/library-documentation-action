# How to cut a library-documentation-action release

This document is aimed at members of the team who might be cutting a release of library-documentation-action  . It serves as a checklist that can take you through doing a release step-by-step.

## Releasing

There's no release process library-documentation-action. New `release` and `latest` docker images are created each time a new nightly or release version of ponyc is created.

We used to have a release process for the library documentation action, but each time there was a breaking change in ponyc, we had to create a new version of the library-documentation-action and every user had to update the version they were using.  Now, on each release a new version is created.
