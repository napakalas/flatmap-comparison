#!/bin/sh

poetry install

git clone git@github.com:AnatomicMaps/flatmap-maker.git mapmaker
cd mapmaker
poetry install
