#!/usr/bin/python
# encoding: utf8

import argparse
import logging
import os
from release_helper.config import make_config, get_project, get_repos, get_releases, get_output_filenames
from release_helper.collect import collect
from release_helper.render import make_html, make_notes
import BaseHTTPServer
import SimpleHTTPServer


def get_args():
    """
    Build up and parse commandline
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="set debug loglevel", action="store_true")
    parser.add_argument("-C", "--configs", help="comma-separated list of config files")

    parser.add_argument("-c", "--collect", help="collect github repository information", action="store_true")
    parser.add_argument("-r", "--render", help="render html release overview", action="store_true")

    parser.add_argument("-w", "--web", help="start simple webserver", action="store_true")
    parser.add_argument("-p", "--port", help="webserver port", default=8000)

    parser.add_argument("-n", "--notes", help="Generate the releasenotes", action="store_true")
    parser.add_argument("--milestone", help="Milestone to use (for releasenotes)")
    parser.add_argument("--notestemplate", help="TT template to use for the releasenotes", default='quattor_releasenotes')

    args = parser.parse_args()
    return args


def main():
    logger = logging.getLogger()
    lvl = logging.INFO

    args = get_args()
    if args.debug:
        lvl = logging.DEBUG

    logger.setLevel(lvl)

    cfgs = None
    if args.configs:
        cfgs = args.configs.split(',')


    use_github = any([getattr(args, x) for x in ('collect',)])

    # Do not unneccesiraly gather GH data
    make_config(cfgs=cfgs, use_github=use_github)

    repos = get_repos()
    project = get_project()
    releases = get_releases()

    basedir, filenames = get_output_filenames()

    if not os.path.isdir(basedir):
        os.mkdir(basedir)

    logging.debug('Release helper start')
    if args.collect:
        logging.info('Collect')
        collect(repos, filenames)

    if args.render:
        logging.info('Render')
        make_html(project, releases, filenames)

    if args.notes:
        logging.info("Release notes using milestone %s and template %s", args.milestone, args.notestemplate)
        make_notes(project, args.milestone, args.notestemplate, filenames)

    logging.debug('Release helper end')

    if args.web:
        os.chdir(basedir)
        logging.debug('Starting webserver on port %s from basedir %s, running forever', args.port, basedir)
        server_address = ('', int(args.port))

        HandlerClass = SimpleHTTPServer.SimpleHTTPRequestHandler
        HandlerClass.protocol_version = "HTTP/1.0"
        httpd = BaseHTTPServer.HTTPServer(server_address, HandlerClass)
        httpd.serve_forever()

if __name__ == '__main__':
    main()
