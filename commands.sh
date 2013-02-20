#!/bin/bash

BUILD_FILES=(caiman docs README.rst)

(
set -e
    git checkout gh-pages
    git checkout develop "${BUILD_FILES[@]}"
    git reset HEAD
    cd docs
    make html
    cd ..
    rsync -urv docs/_build/html/ .
    rm -r "${BUILD_FILES[@]}"
    git add -A
    git commit -m "Generated docs for $(git log develop -1 --oneline --abbrev-commit)"
    echo git push
    git checkout develop
)
