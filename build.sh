#!/bin/bash
echo "===> cleaning the dist folder if exists"
rm -rf dist/*
echo "===> creating the dist folder if not exists"
mkdir -p dist/get2unix/logs dist/get2unix/tmp/vuls_conf
touch dist/get2unix/logs/ldap.log
echo "===> copy app files"
cp -rf apps conf get2unix libs static templates utils docker-compose.yml Dockerfile manage.py redis.conf requirements.txt dist/get2unix
echo "===> switch to dist/get2unix"
cd dist/get2unix
echo "===> changing the running env to poc"
sed -i "s/RUNNING_ENV = 'dev'/RUNNING_ENV = 'poc'/g" get2unix/settings.py
#echo "===> build docker image"
#docker build -t get2unix:0.2 .
echo "===> switch to dist/"
cd ../
#echo "===> exporting docker image"
#docker save get2nix:0.2 | gzip > get2unix_0.2.img.gz
echo "===> packing app files"
tar Jcvf get2unix.txz get2unix
echo "===> cleanup temporary files"
rm -rf get2unix