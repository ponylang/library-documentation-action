FROM ponylang/shared-docker-ci-release-a-library:release

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
