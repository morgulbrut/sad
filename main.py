#!/bin/env python3

import json
import subprocess
import os
import colorlog
import collections
import re
import argparse


handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s: %(message)s'))

logging = colorlog.getLogger('-')
logging.addHandler(handler)

def include(md_file):
    logging.info('Including...')
    output = []
    with open(md_file) as f:
        for line in f.readlines():
            if line.strip().lower().startswith('#include'):
                output.append(include(line.split()[1]))
            else:
                output.append(line)
    return ''.join(output)
    

def replace_lut(md, lut):
    logging.info('Replacing...')
    logging.debug(md)
    for k in lut.keys():
        logging.debug('Replacing: {} => {}'.format(k, lut[k]))
        md = md.replace(k, lut[k])
    with open('tmpfile', 'w') as t:
        t.write(md)
    return t.name


def escape_latex(md_file):
    logging.info('Escaping LaTeX')
    with open(md_file) as f:
        f = f.read()
        f = re.sub(r'(\\[\w\{\}\[\]]*)',r'`\1`',f)
    with open('tmpfile', 'w') as t:
        t.write(f)
    return t.name


def execute_exernal(cmd):
    logging.info('Executing: {}'.format(cmd))
    subprocess.call(cmd, shell=True)


def read_json(json_file):
    logging.info('Reading {}'.format(json_file))
    try:
        json_data = open(json_file).read()
    except FileNotFoundError:
        logging.warning('{} not found'.format(json_file))
        init_config()
        logging.warning('Please rerun to compile your document(s)')
        quit()
    return json.loads(json_data)

def init_config():
    logging.info('Setting up new settings.json')
    conf={'replacements':{},'variables':['lang=de-CH','papersize=A4','fontsize=10pt','documentclass=scrartcl','mainfont=Linux Libertine O','mainfontoptions=Numbers=OldStyle','mainfontoptions=Ligatures=Discretionary','sansfont=Linux Biolinum','sansfontoptions=Numbers=OldStyle'],'extensions':['yaml_metadata_block'],'options':{'numbered_headings':'True','toc':'True','lof':'False','lot':'False','verbose':'False',},'loglevel':'INFO','files': [],}
    for file in os.listdir():
        (name,ext)=os.path.splitext(file)
        if ext == '.md':
            conf['files'].append({'in_file':file,'out_file':name+'.pdf','template':'default.latex'})
    with open('settings.json','w') as f:
        json.dump(conf,f)
    return conf

def options(settings):
    ret = []
    try:
        if 'true' in settings['options']['toc'].lower():
            ret.append('--variable toc')
            logging.debug('Adding option toc')
    except KeyError as e:
        logging.debug(e)
    try:
        if 'true' in settings['options']['lof'].lower():
            ret.append('--variable lof')
            logging.debug('Adding option lof')
    except KeyError as e:
        logging.debug(e)
    try:
        if 'true' in settings['options']['lot'].lower():
            ret.append('--variable lot')
            logging.debug('Adding option lot')
    except KeyError as e:
        logging.debug(e)
    try:
        if 'true' in settings['options']['verbose'].lower():
            ret.append('--verbose')
            logging.debug('Adding option verbose')
    except KeyError as e:
        logging.debug(e)
    try:
        if 'true' in settings['options']['numbered_headings'].lower():
            ret.append('-N')
            logging.debug('Adding option N')
    except KeyError as e:
        logging.debug(e)

    return ' '.join(ret)


def deep_update(source, overrides):
    for key, value in overrides.items():
        if isinstance(value, collections.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source


def generate_output(in_file, out_file, settings, template=''):
    path,ext = os.path.splitext(out_file)
    if ext == '.pdf':
        temp_file = replace_keys(in_file, settings['replacements'])
    if ext == '.md':
        with open('tmpfile', 'w') as t:
            temp_file = escape_latex(in_file)
    logging.info('Generating output...')
    cmd = ['pandoc {}'.format(temp_file)]
    cmd.append('-o {}'.format(out_file))

    if ext == '.pdf':
        cmd.append('--pdf-engine=xelatex')
        cmd.append('--template={}'.format(template))
        in_format = ['--from markdown']
        for extension in settings['extensions']:
            logging.debug('Adding extension: {}'.format(extension))
            in_format.append('+{}'.format(extension))
        cmd.append(''.join(in_format))
        cmd.append(options(settings))
        for variable in settings['variables']:
            logging.debug('Adding variable {}={}'.format(
                variable, settings['variables'][variable]))
            cmd.append('--variable {}="{}"'.format(variable,settings['variables'][variable]))
    if ext == '.md':
        cmd.append('-t gfm')
    execute_exernal(' '.join(cmd))
    os.remove(temp_file)


def main():
    parser = argparse.ArgumentParser(description="Run it once to generate a initial settings.json file. Review it afterwards if it suits your use. By default PDFs for every md found in the working directory will be generated")
    parser.add_argument("-i","--init", help="Writes a new default settings.json. Overwrites any present one",action="store_true")
    parser.add_argument(
        "-b", "--beamer", help="Generates beamer presentation.",action="store_true")
    args = parser.parse_args()
    settings = (read_json('settings.json'))
    logging.setLevel(settings['loglevel'])
    files = settings['files']

    if args.init:
        init_config()
        quit()



    for f in files:
        try:
            generate_output(f['in_file'], f['out_file'], settings, f['template'])
        except KeyError:
            try:
                generate_output(f['in_file'], f['out_file'],settings)
            except Exception as e:
                logging.critical(e)


if __name__ == '__main__':
    main()