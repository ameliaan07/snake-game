#!/bin/bash

# 清理旧的构建文件
rm -rf build docs
mkdir -p docs

# 构建
pygbag main.py

# 复制文件
cp -r build/web/* docs/
touch docs/.nojekyll
