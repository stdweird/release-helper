Description
===========

Release-helper is a python tool that helps you manage large number of
github repositories by controlling milestones and labels,
and creating a overiew of the release process.

Configfile
==========

Username / token are best stored in minimal config file,
and used together with project config file.
This allows you to share the project configfile,
without compromising authentication details.

Example:
    release-helper.py --configs=.secret/credentials.cfg,project.cfg --collect

Commands
========
 * collect: gather the data from github, creates JSON file (most other steps will use this JSON file)
 * render: generate the release notes overview and to discuss
 * notes: generate the release notes (there's a *notestemplate* option to select a different template)
   Example:
       release-helper.py  --configs=.secret/credentials.cfg,quattor.cfg --notes --milestone 16.6
 * milestones: configure milestones due date on release data (or generated if milestone is not in release data)
     * TODO: Missing the ability to open/close milestones
 * labels: configure (add or update; no remove) the labels
 * bump: advanced: bump/shift the milestones by `--months` number of months (default 2).
     Generates and prints the release section data with updated dates.

Local usage
===========
You cannot use `file:///path/to/project/index.html` because some of the css and javascript url use
protocol relative urls, and would require that you install those also in the pooject dir.

* generate the required html and json using and start webserver using `--render --web` option
* got to url `http://localhost:8000` (and `http://localhost:8000/to_discuss`)

Example release page
====================

Example:
    [quattor release overview]:(http://quattor.org/release)
