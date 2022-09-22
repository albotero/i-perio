#!/bin/bash

# Processes all scss files to css
# Arg1 : css dir

base=`pwd`
scss="../../scss/"

titleformat="\n\033[1m%s\033[0m\n"
format=" ╎  %-18.18s ╎  %-18.18s ╎  %-7.7s ╎\n"

lines() {
  printf "%2s" " +"
  printf "%.0s–" {1..21}
  printf "%s" "+"
  printf "%.0s–" {1..21}
  printf "%s" "+"
  printf "%.0s–" {1..10}
  printf "%s" "+"
  printf "\n"
}

cd $1
printf "$titleformat" "Compilando CSS ..."
lines
printf "$format" "     ORIGEN" "     DESTINO" "ESTADO"
lines

for f in `ls $scss`
do
  css_file="${f%.scss}.css"
  ~/dart-sass/sass --no-source-map "${scss}${f}" "$css_file"
  printf "$format" $f $css_file "  ok"
  lines
done

printf "$titleformat" "Iniciando servidor ..."
cd $base
gunicorn -c gunicorn.config.py
