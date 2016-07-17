---
layout: article
title: myproject 16.6 released
category: news
author: James Adams
---

Packages are available from our [yum repository](http://yum.quattor.org/16.6/),
both the RPMs and the repository metadata are signed with
[my GPG key](http://yum.quattor.org/GPG/RPM-GPG-KEY-quattor-jrha).

As always, many thanks to everyone who contributed!
We merged 5 pull requests and resolved 1 issues.

The next release should be 16.8,
take a look at the [backlog](http://www.quattor.org/release/) to see what we're working on.

Backwards Incompatible Changes
------------------------------

### CAF
* [**Lock:** handle existing old-style locks](https://github.com/quattor/CAF/pull/173)

Changelog
---------

### CAF
* [Add PyCharm and Eclipse files to gitignore](https://github.com/quattor/CAF/pull/174)
* [**Lock:** handle existing old-style locks](https://github.com/quattor/CAF/pull/173)

### CCM
* [**CCM:** fetchProfile should close all CAF::File* instances ](https://github.com/quattor/CCM/pull/101)
* [**ProfileCache:** Lock use reporter instance for reporting](https://github.com/quattor/CCM/pull/111)
* [bump build-tools to 1.49](https://github.com/quattor/CCM/pull/99)

