#!/bin/bash
if [ -z $1 ]; then
  echo -e "You must supply the package name eg: (elcapitan-environment.pkg)"
  exit
fi
if ! [ -f $1 ]; then
  echo -e "Package: "$1" not located in current directory"
  exit
fi
# Clean a previous build
if [ -d ./dist ]; then 
  echo 'deleting dist'
  rm -rf ./dist
fi
if [ -d ./build ]; then 
  echo 'deleting build'
  rm -rf ./build
fi
if [ -f elcapitan-environment.dmg ]; then
  echo 'deleting elcapitan-environment.dmg'
  rm -f elcapitan-environment.dmg
fi
if [ -f rw.elcapitan-environment.dmg ]; then
  echo 'deleting rw.elcapitan-environment.dmg'
fi

mkdir dist
cp $1 dist/

echo -e '\nBuilding elcapitan-environment.dmg'
sleep 1
./build_dmg/create-dmg --background ./moose_package.png --icon $1 230 150 --volname "MOOSE Package" --icon-size 120 elcapitan-environment.dmg ./dist

echo -e '\nDone.'
