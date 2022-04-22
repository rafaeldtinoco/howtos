#!/bin/sh

#set -eufo pipefail

if [ "$#" -ne 2 ]; then
    echo "usage: $0 source_repo_url target_repo_url" >&2
    exit 1
fi

SOURCE_URL="$1"
TARGET_URL="$2"
WORKDIR="$(mktemp -d)"

echo "Cloning from ${SOURCE_URL} into ${WORKDIR}..."

git init --bare "${WORKDIR}"
cd "${WORKDIR}"

git config remote.origin.url "${SOURCE_URL}"
git config --add remote.origin.fetch '+refs/heads/*:refs/heads/*'
git config --add remote.origin.fetch '+refs/tags/*:refs/tags/*'
git config --add remote.origin.fetch '+refs/notes/*:refs/notes/*'
git config remote.origin.mirror true
git fetch --all

echo ""
echo "Cloned to ${WORKDIR}; pushing to ${TARGET_URL}"

git push --mirror "${TARGET_URL}"

echo ""
echo "Cleaning up temporary directory ${WORKDIR}..."

rm -rf "${WORKDIR}"

echo "Done."
