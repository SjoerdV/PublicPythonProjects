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
This program will add keywords (tags) to Jekyll posts (ie. markdown files with YAML frontmatter).
It is designed to work in conjunction with a VSCode 'Tasks' and accompanying 'Keyboard Shortcut'.
An example 'tasks.json' file is provided in the same directory of this script. NOTE: You might need to merge this configuration with your existing Static Site tasks configuration file.
An example 'keybindings.json' file is provided in the same directory of this script. NOTE: you will need to copy this keybinding configuration to your own VSCode 'User' configuration.

Prerequisites:
* Python3 3.9+
* pip install markdown
* pip install beautifulsoup4
* pip install python-frontmatter
* pip install keyphrase-vectorizers
* pip install keybert

References:
* Workflow stuff
** VSCode, Run multiple statements for one action: https://github.com/microsoft/vscode/issues/871#issuecomment-488355245
** Clean Markdown to Plain Text: https://stackoverflow.com/a/761847
** PascalCase: https://stackoverflow.com/questions/8347048/how-to-convert-string-to-title-case-in-python
* NLP stuff
** Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/
** KeyphraseVectorizers: https://github.com/TimSchopf/KeyphraseVectorizers
** KeyBert: https://github.com/MaartenGr/keyBERT
** Combining KeyBERT and KeyphraseVectorizers: https://towardsdatascience.com/enhancing-keybert-keyword-extraction-results-with-keyphrasevectorizers-3796fa93f4db
** KeyBERT introduce diversity in resulting keywords: https://towardsdatascience.com/how-to-extract-relevant-keywords-with-keybert-6e7b3cf889ae

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
add_keyphrases_to_jekyll_blog_post.py -i "/home/user/full_path_to_jekyll_site/_posts/2022-12-21-post-my-post.md"
This will start the process of adding keywords to the YAML frontmatter of the post using the settings specified in the 'nlp.json' file.
"""


# Import modules
from __future__ import annotations
import sys
import getopt
import re
import json
from io import BytesIO
from markdown import markdown
from bs4 import BeautifulSoup
import frontmatter
from keyphrase_vectorizers import KeyphraseCountVectorizer
from keybert import KeyBERT


# Define functions
def md_to_text(md_text):
    """_summary_

    Args:
        md (_type_): _description_

    Returns:
        _type_: _description_
    """
    html = markdown(md_text)
    soup = BeautifulSoup(html, features='lxml')
    return soup.get_text()


def main(argv):
    """_summary_

    Args:
        argv (_type_): _description_
    """
    # Init Variables
    input_file_path: str | None = None
    help_message: str = 'add_keyphrases_to_jekyll_blog_post.py -i <input_absolute_file_path>'
    numberof_phrases: int | None = None
    keyphrase_count_vectorizer_args: dict | None = None
    keybert_args: dict | None = None

    # Processing CLI input
    try:
        opts, args = getopt.getopt(argv,"hi:",["help","in="])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)
    if not opts:
        print(help_message)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_message)
            sys.exit()
        elif opt in ("-i", "--in"):
            try:
                input_file_path = str(arg)
            except Exception as error:
                print(error)
                sys.exit(2)
            if re.search(r'.md$',input_file_path) is None:
                print('Input file is not a markdown file (with .md extension). Exiting...')
                sys.exit(2)
    print ('Input file path is:', input_file_path, '\r\n')

    # Load JSON settings
    ## Opening JSON settings file
    json_data_file = open('nlp.json',encoding="utf8")
    ## Returns JSON object as a dictionary
    json_object = json.load(json_data_file)

    # Set NLP Variables
    try:
        numberof_phrases = int(json_object['settings']['key_phrase_output_count'])
        keyphrase_count_vectorizer_args = json_object['settings']['nlp_models'][0]['arguments']
        print(keyphrase_count_vectorizer_args)
        keybert_args = json_object['settings']['nlp_models'][1]['arguments']
        print(keybert_args)
    except Exception as error:
        print(error)
        sys.exit(2)

    # Open the Post Markdown file
    post = frontmatter.load(input_file_path)
    #print(post.content)
    #print(post.metadata)
    #sorted(post.keys())

    # Fetch current tags
    overwrite = 'N'
    try:
        current_tags = post["tags"]
        if len(current_tags) > 0:
            overwrite = input('\r\nWARNING: Tags '+str(current_tags)+' are already present. Do you wish to overwrite? (Y/N)')
    except (KeyError, TypeError):
        print("'tags' metdata does not exist. Continuing...")
        overwrite = 'Y'

    if re.match('[y]', overwrite, re.IGNORECASE):
        # Clean up the MarkDown Jekyll document
        plain_text_md = md_to_text(post.content)
        plain_text_md = re.sub(r"{{.*}}", '', plain_text_md)
        plain_text_md = re.sub(r"{%.*%}", '', plain_text_md)
        plain_text_md = re.sub(r"(\[\^\d+\](:\s)?)", '', plain_text_md)
        plain_text_md = re.sub(r"\[(.*)\]:\s", r"\1: ", plain_text_md)
        plain_text_md = re.sub(r"```.*```", '', plain_text_md, flags=re.S)
        print("\r\nPlain Text MD Document:",plain_text_md)

        # Load the document as list
        docs = []
        docs.append(plain_text_md)

        # Init default vectorizer
        try:
            #keyphrase_count_vectorizer_args[0] = nlp
            vectorizer = KeyphraseCountVectorizer(**keyphrase_count_vectorizer_args)
        except Exception as error:
            print("KeyphraseCountVectorizer error:", error)
            sys.exit(2)

        # Fit the vectorizer with key phrases from the document
        vectorizer.fit(docs)

        # After learning the keyphrases, they can be returned.
        vectorized_keyphrases = vectorizer.get_feature_names_out()
        print("\r\nVectorized Key Phrases:",vectorized_keyphrases)

        # Init KeyBERT
        try:
            kw_model = KeyBERT(**keybert_args)
        except Exception as error:
            print("KeyBERT error:", error)
            sys.exit(2)

        # Use keyphrase vectorizer to decide on suitable keyphrases
        # adding ', use_mmr=True, diversity=0.3' to the settings and varying the diversity may prove useful at some point.
        keyphrases = kw_model.extract_keywords(docs=docs, top_n=numberof_phrases, vectorizer=vectorizer)
        print("\r\nKeyBERT Key Phrases:",keyphrases)

        # Transform key phrases to PascalCase
        transformed_keyphrases = []
        for keyphrase in keyphrases:
            keyphrase_pascal_case = ''.join(x for x in keyphrase[0].title() if not x.isspace())
            transformed_keyphrases.append(keyphrase_pascal_case)
        print("\r\nPascalCase Key Phrases:",transformed_keyphrases)

        # Save new tags to existing post object
        post.metadata["tags"] = transformed_keyphrases

        # Write updated post to disk
        file_io = BytesIO()
        frontmatter.dump(post, file_io)
        text_file = open(input_file_path, "w", encoding="utf-8")
        update_file = text_file.write(file_io.getvalue().decode('utf-8'))
        text_file.close()


# Start main thread
if __name__ == "__main__":
    main(sys.argv[1:])
