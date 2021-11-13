# semver.py

Semantic Versioning (semver.org) を扱う Python ライブラリです。

# 開発情報

    # Docker イメージをビルドする
    make docker-build

    # コンテナ内で試行錯誤する
    docker run -it --rm -v $(pwd):/app:ro semver-python:latest bash

    # sphinx-quickstart
    make docs

    # テストを実行する
    make test

