---
title:  'Public Python Projects'
author:
- Sjoerd de Valk, SPdeValk Consultancy
date: 2022-12-21 22:35:00
last_modified_at: 2023-09-05T00:41:58+02:00
keywords: [linux, tooling, markdown, python]
abstract: |
  This document is about briefly explaining the scripts present in this repository.
permalink: /index.html
---
[![GitHub License](https://img.shields.io/github/license/SjoerdV/PublicPythonProjects)](https://github.com/SjoerdV/PublicPythonProjects/blob/main/LICENSE)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FSjoerdV%2FPublicPythonProjects&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/SjoerdV/PublicPythonProjects)
[![GitHub All Stars](https://img.shields.io/github/stars/SjoerdV/PublicPythonProjects?label=stars)](https://github.com/SjoerdV/PublicPythonProjects/stargazers)
[![GitHub All Forks](https://img.shields.io/github/forks/SjoerdV/PublicPythonProjects?label=forks)](https://github.com/SjoerdV/PublicPythonProjects/network/members)
[![GitHub Latest Release](https://img.shields.io/github/v/release/SjoerdV/PublicPythonProjects?include_prereleases&color=red)](https://github.com/SjoerdV/PublicPythonProjects/releases)
[![GitHub All Downloads](https://img.shields.io/github/downloads/SjoerdV/PublicPythonProjects/total?label=downloads)](https://github.com/SjoerdV/PublicPythonProjects/releases)

## PublicPythonProjects

### Summary

This repository contains folders for each Python 3 (compatible with at least version 3.9 and higher) scripting project. The main `.py` file in each folder will contain all instructions necessary.

I will make an effort to make all scripts cross-platform compatible and test the scripts under both Linux (Debian-based) and Windows. The scripts should also work under MacOS, but I will not test this explicitly (and will never do).

At the moment the following Projects are available.

* [svg2png](https://github.com/SjoerdV/PublicPythonProjects/tree/main/svg2png)
  * this program will convert any svg image to png. For more information see `svg2png.py`.
  * Reference: [Blog Post](https://www.spdevalk.nl/blog/post-a-new-public-github-repository-python/)
* [appindicator](https://github.com/SjoerdV/PublicPythonProjects/tree/main/appindicator)
  * this program will run a system tray icon which will detect if a certain process is running. It reports to the Desktop notification area and change the trays color when the process is found (or killed). It also features a right click context menu to kill all the processes of the kind it is monitoring. For more information see `appindicator.py`.
  * Reference: [Blog Post](https://www.spdevalk.nl/blog/post-a-new-public-github-repository-python/)
* [add_keyphrases_to_jekyll_blog_post](https://github.com/SjoerdV/PublicPythonProjects/tree/main/add_keyphrases_to_jekyll_blog_post)
  * this program will add or update the 'tags' metadata key that can be found in the YAML frontmatter of Jekyll static website pages. These pages are markdown formatted pages (with .md extension) and contains liquid elements and said YAML frontmatter. The KeyBERT and KeyphraseVectorizers modeling tools, being fed their configuration through an external JSON file, are used to generate these tags. Extensive documentation is available for both these tools to further your implementation. For more information see `add_keyphrases_to_jekyll_blog_post.py`.
  * Reference: [Blog Post](https://www.spdevalk.nl/blog/post-adding-key-phrases-to-jekyll-blog-posts-_-the-offline-edition/)
* [mastodon_archiver](https://github.com/SjoerdV/PublicPythonProjects/tree/main/mastodon_archiver)
  * this program will make backups of your mastodon account(s) and clean-up certain collections that are more than 8 weeks old.
  * Reference: [Original Repo](https://github.com/kensanata/mastodon-archive)
* [captcha_generator](https://github.com/SjoerdV/PublicPythonProjects/tree/main/captcha_generator)
  * this program will create a CAPTCHA version of text entered by you
  * Reference: [Blog Post](https://www.makeuseof.com/python-captcha-create/)
* [auto_discussion_for_jekyl_blog_post](https://github.com/SjoerdV/PublicPythonProjects/tree/main/auto_discussion_for_jekyl_blog_post)
  * this is a script for adding a GitHub Discussion for each Blog Post in a GitHub Pages repository and makes use of GitHub GraphQL. For more information see `auto_discussion_for_jekyl_blog_post.py`.
  * Reference: [Blog Post](https://www.spdevalk.nl/blog/post-giscus-for-comments/)

### Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

#### [Unreleased]

#### [2.0.0] - 2023-09-05

##### Added

* Added '`add_keyphrases_to_jekyll_blog_post`'
* Added '`mastodon_archiver`'
* Added '`captcha_generator`'
* Added '`auto_discussion_for_jekyl_blog_post`'

##### Changed

* Nothing

##### Removed

* Nothing

### Credits

All Python developers, making this an awesome scripting language.

#### [1.0.0] - 2022-12-21

##### Added

* Initial Release with initial project folder structure.

##### Changed

* Nothing

##### Removed

* Nothing

### Credits

All Python developers, making this an awesome scripting language.
