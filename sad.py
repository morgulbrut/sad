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
    output = []
    with open(md_file) as f:
        try:
            for line in f.readlines():
                if line.strip().lower().startswith('#include'):
                    logging.info('Including {}'.format(line.split()[1]))
                    output.append(include(line.split()[1]))
                else:
                    output.append(line)
        except UnicodeDecodeError:
            pass
        output.append('\n\n')
    return ''.join(output)


def replace_lut(md, lut):
    logging.info('Replacing... ("replacements" in json)')
    for k in lut.keys():
        logging.debug('Replacing: {} => {}'.format(k, lut[k]))
        md = md.replace(k, lut[k])
    return ''.join(md)


def set_pdf_engine(pandoc_ver):
    if pandoc_ver == 1:
        return '--latex-engine'
    else:
        return '--pdf-engine'


def get_pandoc_vers():
    logging.info('Getting pandoc version...')
    try:
        process = subprocess.Popen(['pandoc', '-v'], stdout=subprocess.PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
        output = str(output, 'UTF-8').split('\n')[0].lower()
    except FileNotFoundError:
        logging.critical('Pandoc not found, please install pandoc')
        quit()
    logging.info('Found: {}'.format(output))
    if 'pandoc 2' in output:
        return 2
    else:
        return 1


def escape_latex(md):
    logging.info('Escaping LaTeX')
    return re.sub(r'(\\[\w\{\}\[\]]*)', r'`\1`', md)


def execute_exernal(cmd):
    logging.info('Executing: {}'.format(cmd))
    subprocess.call(cmd, shell=True)


def read_json(json_file):
    logging.info('Reading {}'.format(json_file))
    try:
        json_data = open(json_file).read()
    except FileNotFoundError:
        logging.warning('{} not found'.format(json_file))
        logging.warning('Use sad -i to generate a initial settings.json')
        quit()
    try:
        return json.loads(json_data)
    except json.decoder.JSONDecodeError:
        logging.critical('{} not formated proprely'.format(json_file))
        quit()


def init_config():
    logging.info('Setting up new settings.json')
    conf = {'replacements': {}, 'variables': ['lang=de-CH', 'papersize=A4', 'fontsize=10pt', 'documentclass=scrartcl', 'mainfont=Linux Libertine O', 'mainfontoptions=Numbers=OldStyle', 'mainfontoptions=Ligatures=Discretionary', 'sansfont=Linux Biolinum',
                                              'sansfontoptions=Numbers=OldStyle', 'urlcolor=blue'], 'extensions': ['yaml_metadata_block'], 'options': {'numbered_headings': 'True', 'toc': 'True', 'lof': 'False', 'lot': 'False', 'verbose': 'False', }, 'loglevel': 'INFO', 'files': [], }
    for file in os.listdir():
        (name, ext) = os.path.splitext(file)
        if ext == '.md':
            conf['files'].append(
                {'in_file': file, 'out_file': name + '.pdf', 'template': 'default.latex'})
    with open('settings.json', 'w') as f:
        json.dump(conf, f, indent=4)
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


def generate_pdf(in_file, out_file, settings, template='', beamer=False):
    cmd = ['pandoc {}'.format(in_file)]
    cmd.append('-o {}'.format(out_file))
    if beamer:
        cmd.append('-t beamer')

        for variable in settings['variables']:
            logging.debug('Adding variable {}'.format(variable))
            cmd.append('--variable "{}"'.format(variable))
    else:
        cmd.append('--template={}'.format(template))

        for variable in settings['variables']:
            logging.debug('Adding variable {}'.format(variable))
            cmd.append('--variable "{}"'.format(variable))
    in_format = ['--from markdown']
    for extension in settings['extensions']:
        logging.debug('Adding extension: {}'.format(extension))
        in_format.append('+{}'.format(extension))
    pdf_engine = (set_pdf_engine(get_pandoc_vers()))
    cmd.append('{}=xelatex'.format(pdf_engine))
    cmd.append(''.join(in_format))
    cmd.append(options(settings))
    execute_exernal(' '.join(cmd))


def generate_output(in_file, out_file, settings, template=''):
    path, ext = os.path.splitext(out_file)
    logging.info('Generating output...')
    logging.debug('{} => {}'.format(in_file, out_file))
    md = include(in_file)
    if ext == '.pdf':
        with open('tmpfile', 'w') as f:
            f.write(replace_lut(md, settings['replacements']))
        generate_pdf('tmpfile', out_file, settings, template)
    if ext == '.md':
        with open('tmpfile', 'w') as f:
            f.write(escape_latex(md))
        cmd = ['pandoc {}'.format('tmpfile')]
        cmd.append('-o {}'.format(out_file))
        cmd.append('-t gfm')
        execute_exernal(' '.join(cmd))
    if ext == '.docx':
        with open('tmpfile', 'w') as f:
            f.write(replace_lut(md, settings['replacements']))
            f.write(escape_latex(md))
        cmd = [
            'pandoc -s --reference-doc {} -o {} {}'.format(template, 'tmpfile', in_file)]
        execute_exernal(' '.join(cmd))

    if ext == '.revealjs':
        if not os.path.isdir('reveal.js'):
            logging.debug('Try to download reveal.js')
            try:
                execute_exernal('git clone https://github.com/hakimel/reveal.js.git')
            except:
                logging.warning("Failed getting reveal.js. You should get it yourself")

        with open('tmpfile', 'w') as f:
            f.write(md)
        cmd = ['pandoc {}'.format('tmpfile')]
        cmd.append('-t revealjs -s -o {}.html'.format(os.path.splitext(out_file)[0]))
        execute_exernal(' '.join(cmd))
    os.remove('tmpfile')


def main():
    parser = argparse.ArgumentParser(
        description="Run it once to generate a initial settings.json file. Review it afterwards if it suits your use. By default PDFs for every md found in the working directory will be generated")
    parser.add_argument(
        "-i", "--init", help="Writes a new default settings.json. Overwrites any present one", action="store_true")
    parser.add_argument(
        "-b", "--beamer", help="Generates beamer presentation. Tries to get settings from slides.json", action="store_true")
    parser.add_argument(
        "-f", "--file", help="Just process a given specific file.")
    args = parser.parse_args()

    if args.init:
        init_config()
        quit()


    if args.beamer:
        settings = (read_json('slides.json'))
    else:
        settings = (read_json('settings.json'))

    logging.setLevel(settings['loglevel'])

    if args.file:
        infile = args.file
        (name, ext) = os.path.splitext(infile)
        files = [{'in_file': args.file, 'out_file': name +
                  '.pdf', 'template': 'default.latex'}]
    else:
        files = settings['files']


    for f in files:
        try:
            if args.beamer:
                generate_pdf(f['in_file'], f['out_file'],
                             settings, f['template'], beamer=True)
            else:
                generate_output(f['in_file'], f['out_file'],
                                settings, f['template'])
        except KeyError:
            try:
                generate_output(f['in_file'], f['out_file'], settings)
            except Exception as e:
                logging.critical(e)


if __name__ == '__main__':
    main()
