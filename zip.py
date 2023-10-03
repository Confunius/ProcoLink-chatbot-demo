from zipfile import ZipFile
import os, sys

#unzip Healthy-Living.zip
zipref = ZipFile('/workspaces/Sunset.AI-demo/Healthy-Living-main (1).zip', 'r')
zipref.extractall()