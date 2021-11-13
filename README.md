# semver.py

Semantic Versioning (semver.org) を扱う Python ライブラリです。

# 開発情報

    # Docker イメージをビルドする
    docker build -t semver-python:latest .

    # テストを実行する
    docker run -it --rm -v $(pwd):/app:ro semver-python:latest python -m unittest discover -s test

