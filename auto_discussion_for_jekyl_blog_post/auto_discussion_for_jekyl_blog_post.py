#!/usr/bin/env python3

"""
License:
This file is part of the 'PublicPythonProjects' distribution (https://github.com/sjoerdv or http://sjoerdv.github.io).
Copyright (C) 2022  Sjoerd de Valk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Description:
This is a script for adding a GitHub Discussion for each Blog Post in a GitHub Pages repository.

Prerequisites:
* Python3 3.9+

References:
https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions
https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad
https://gist.github.com/StevenACoffman/ffcc754f7f84a69efcb84442eca302e0
https://github.com/giscus/giscus#readme

Image Sources:
None

Tested on:
* Linux
** OS: LMDE 5 (elsie) x86_64
** Kernel: 6.0.0-0.deb11.2-amd64
** WM: Cinnamon 5.4.12
** Python3: 3.9.2
* Windows
** OS: Windows 10 21H2
** Python3: 3.9.5

Example:
auto_discussion_for_jekyl_blog_post.py
"""
from __future__ import annotations
import sys
from datetime import datetime, timezone
import subprocess
import time
import logging
import re
import requests


#######################################
# LOAD ACCESS TOKEN AND OTHER VARIABLES
# IMPORTANT: You will need to have 'pass' installed and your keyring unlocked, this will fetch the 6 variables securely.
# IMPORTANT: Variable names should be identical to the 'pass' entry keys (left of the equals sign)
# PASS ENTRY EXAMPLE (ie. password is always on line 1):
"""
repo_owner=myorg
blog_repo_name=myorg.github.io
blogsite_url=https://www.myblogsite.com/
discussion_repo_name=myorg.github.io-comments
discussion_repo_id=vk_klhFkf76cn
discussion_category_id=DIC_jsfbvnJBbvjd98
"""
#######################################
github_token = ""
repo_owner = ""
blog_repo_name = ""
discussion_repo_name = ""
discussion_repo_id = ""
discussion_category_id = ""
blogsite_url = ""
real_requests_post = requests.post

# The below routine is valid when using a CLI password manager like 'pass'
p1 = subprocess.Popen(
    ["pass", "github/github-pages-auto-discussion"], stdout=subprocess.PIPE)
i = 0
for pass_line in (str(p1.communicate())[3:-10]).split('\\n'):
    #print("line", i, pass_line)
    if i == 0:
        github_token = pass_line
    else:
        var_key = pass_line.split('=')[0]
        var_value = pass_line.split('=')[1]
        locals()[var_key] = var_value
    i = i + 1


##################
# DEFINE FUNCTIONS
##################
def wrap_requests_post(*args, **kwargs):
    """ executes the graphql call and shows rate limit info for each call

    Returns:
        dict: response
    """
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['Authorization'] = 'token ' + github_token
    response = real_requests_post(*args, **kwargs)
    if 'x-ratelimit-used' in response.headers._store:
        print("ratelimit status: used %s of %s. next reset in %s minutes" % (
            response.headers['X-RateLimit-Used'],
            response.headers['X-RateLimit-Limit'],
            datetime.fromtimestamp(int(
                response.headers["X-RateLimit-Reset"]) - time.time(), tz=timezone.utc).strftime("%M:%S")
        ))
    return response


requests.post = wrap_requests_post


#################################
# ROUTINE TO FETCH ALL BLOG POSTS
#################################
query = """
{ repository(owner: "<REPO_OWNER>", name: "<BLOG_REPO_NAME>") {
    object(expression: "master:_posts/") {
        ... on Tree {
            entries {
                name
            }
        }
    }
} }
""".replace("<REPO_OWNER>", repo_owner).replace("<BLOG_REPO_NAME>", blog_repo_name)

# place the call
response = requests.post(
    'https://api.github.com/graphql', json={'query': query})
data = response.json()
# print(data)

# Parse JSON data
try:
    print('Number of posts: ', len(
        data["data"]["repository"]["object"]["entries"]))
except Exception as e:
    logging.error("{e}\nThe data has no items")
    sys.exit(2)

# Transform post names so they correspond to the site Url
blog_items: list = data["data"]["repository"]["object"]["entries"]
expected_titles: list = []
for blog_item in blog_items:
    # remove chars
    name: str = re.sub(r".md$", '', str(blog_item['name'])[11:])
    # add chars
    name = 'blog/' + name + '/'
    expected_titles.append(name)
# print(expected_titles)


##################################
# ROUTINE TO FETCH ALL DISCUSSIONS
##################################
query = """
{ repository(owner:"<REPO_OWNER>", name:"<DISCUSSION_REPO_NAME>") {
    discussions(first: 100, after: null, categoryId: "<CATEGORYID>") {
        totalCount
        edges {
            cursor
            node {
                id
            }
        }
        nodes {
            id
            title
            body
            number
            url
        }
    }
} }
""".replace("<REPO_OWNER>", repo_owner).replace("<DISCUSSION_REPO_NAME>", discussion_repo_name).replace("<CATEGORYID>", discussion_category_id)

# place the call
response = requests.post(
    'https://api.github.com/graphql', json={'query': query})
data = response.json()
# print(data)

# Parse JSON data
try:
    print('Number of discussions: ',
          data["data"]["repository"]["discussions"]["totalCount"])
except Exception as e:
    logging.error("{e}\nThe data has no items")
    sys.exit(2)

discussion_items: list = data["data"]["repository"]["discussions"]["nodes"]
actual_titles: list = []
for discussion_item in discussion_items:
    actual_titles.append(discussion_item['title'])
# print(actual_titles)


###############################################################
# ROUTINE TO ADD NEW DISCUSSIONS FOR BLOGS THAT DO NOT HAVE ONE
###############################################################
for expected_title in expected_titles:
    if expected_title not in actual_titles:
        # set discussion variables
        body = "# " + expected_title + "\n\nAsk me anything about this blog!\n\n" + \
            blogsite_url + expected_title
        query = """
            mutation {
                createDiscussion(input: {repositoryId: "<REPOSITORYID>", categoryId: "<CATEGORYID>", body: "<BODY>", title: "<EXPECTED_TITLE>" }) {
                    discussion {
                        id
                    }
                }
            }
            """.replace("<REPOSITORYID>", discussion_repo_id).replace("<CATEGORYID>", discussion_category_id).replace("<BODY>", body).replace("<EXPECTED_TITLE>", expected_title)
        # print(blogsite_url, expected_title, sep='')
        print('Adding discussion for blog:', expected_title)

        # place the call
        response = requests.post(
            'https://api.github.com/graphql', json={'query': query})
        data = response.json()
        print(data)
