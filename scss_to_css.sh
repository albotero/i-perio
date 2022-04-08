#!/bin/bash

# Processes all scss files to css

scss='scss/'
css='../static/css/'

cd $scss

for f in `ls`
do
  css_file="${css}${f%.scss}.css"
  echo -e "${scss}${f} -> $css_file"
  ~/dart-sass/sass $1 "$f" "$css_file"
done
