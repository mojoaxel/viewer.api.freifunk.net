# -*- coding: utf-8 -*-

import os
import json
import shutil
import sys

from jinja2 import Environment, FileSystemLoader
from urllib2 import urlopen
from datetime import datetime

def is_dict(value):
    return isinstance(value, dict)


env = Environment(loader=FileSystemLoader('templates'))
env.tests['dict'] = is_dict


def gen_bbox(latlon):
    bbox = [latlon[1]-0.05,latlon[0]-0.01,latlon[1]+0.05,latlon[0]+0.01]
    return '%2C'.join(map(str,bbox))


def render_community(template_path, data):
  if 'name' in data:
    community = data['name']
    del data['name']

  if 'url' in data:
    url = data['url']
    del data['url']

  latlon = (float(data['location']['lat']),float(data['location']['lon']))

  template = env.get_template(template_path)
  html = template.render(
            community=community,
            url=url,
            latlon=latlon,
            bbox=gen_bbox(latlon),
            data=data)

  return html.encode('utf-8')


def render_index(template_path, communities):
  template = env.get_template(template_path)
  html = template.render(
    communities=communities,
    now=datetime.now().ctime()
  )

  return html.encode('utf-8')


if __name__ == "__main__":
  build_dir = 'build'

  if len(sys.argv) > 1:
    build_dir = sys.argv[1]

  if not os.path.isdir(build_dir):
    os.makedirs(build_dir)

  # communities
  url = 'https://raw.github.com/freifunk/api.freifunk.net/master/directory/directory.json'
  req = urlopen(url)
  communities = json.load(req)
  entries = {}
  rendered = {}

  for name, url in communities.items():
    print("Collectin data for %s...\t" % name),
    try:
      req = urlopen(url)
      entries[name] = json.load(req)
      print("ok")
    except:
      print("error")

  for name, data in entries.items():
    print("Rendering %s...\t" % name),
    path = os.path.join(build_dir, '%s.html' % name)
    try:
      with open(path,'w') as f:
        f.write(render_community('community.html', data))
        rendered[name] = data
        print("ok")
    except:
        print("error")

  # index
  with open(os.path.join(build_dir, 'index.html'),'w') as f:
    f.write(render_index('index.html', rendered))

  # style
  static_files = os.listdir('static')
  for name in static_files:
      path = os.path.join('static', name)
      if (os.path.isfile(path)):
        shutil.copyfile(path, os.path.join(build_dir, name))
