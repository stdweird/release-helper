Description
===========

Release-helper is a python tool that helps you manage large number of
github repositories by managing milestones and labels,
and creating a overiew of the release process.

Configfile
==========

Example release page
====================

Local usage
===========
You cannot use `file:///path/to/project/index.html` because some of the css and javascript url use
protocol relative urls, and would require that you install those also in the pooject dir.

* generate the required html and json using and start webserver using `--render --web` option
* got to url `http://localhost:8000`
