#!/bin/env python3

import json
import subprocess
import os
import colorlog
import collections
import re

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s: %(message)s'))

logging = colorlog.getLogger('-')
logging.addHandler(handler)


def replace_keys(md_file, lut):
    logging.info('Replacing...')
    with open(md_file) as f:
        f = f.read()
        for k in lut.keys():
            logging.debug('Replacing: {} => {}'.format(k, lut[k]))
            f = f.replace(k, lut[k])
    with open('tmpfile', 'w') as t:
        t.write(f)
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
        logging.critical('Please provide a settings.json file')
        quit()
    return json.loads(json_data)


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
    settings = (read_json('settings.json'))
    try:
        deep_update(settings, read_json(os.getcwd() + '/user_settings.json'))
    except Exception as e:
        logging.warning(e)
    logging.setLevel(settings['loglevel'])
    files = settings['files']
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