#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from transliterate import translit

import glob
import os
import sys
import shutil
import csv
import jinja2

__script_dir__ = os.path.dirname(os.path.realpath(__file__))

class Baka:
    """Бака — от слова «бакалавр», поэтому звучит гордо"""

    subdir = sys.argv[1]
    evenrow = True

    def __init__(self, src_folder, title, supervisor, reviewer):
        self.evenrow = Baka.evenrow = not Baka.evenrow
        self.title = title
        self.fio = src_folder
        self.src_folder = src_folder
        self.dst_prefix = os.path.join(Baka.subdir, translit(src_folder, 'ru', reversed=True).
                                       replace(' ', '_').replace("'","y"))

        self.supervisor = supervisor
        self.reviewer = reviewer
        self.has_slides = True
        self.has_testimonial = True
        self.has_review = True

    @property
    def has_code_archive(self):
        return (self.code_type in ['zip', '7z'])

    @property
    def code_type(self):
        "stops after first matching, even if there are multiple"
        for arname in glob.glob(os.path.join(self.src_folder, 'code.*')):
            if arname.endswith('.zip'):
                return 'zip'
            elif arname.endswith('.7z'):
                return '7z'
            elif arname.endswith('.hyperlink'):
                return 'hyperlink'
            elif arname.endswith('.txt'):
                return 'txt'
        return None

    @property
    def has_code_link(self):
        return self.code_type == 'hyperlink'

    @property
    def has_code_comment(self):
        return self.code_type == 'txt'

    @property
    def code_comment(self):
        if not self.has_code_comment:
            return None
        else:
            with open(os.path.join(self.src_folder, 'code.txt'), encoding='utf-8') as ccf:
                return ccf.readline().strip()

    @property
    def code_link(self):
        if self.has_code_link:
            with open(os.path.join(self.src_folder, 'code.hyperlink')) as hlf:
                return hlf.readline().strip()
        elif self.has_code_archive:
            return self.dst_prefix.replace('\\', '/') + "-code." + self.code_type

    @property
    def text_link(self):
        return self.dst_prefix.replace('\\', '/') + "-text.pdf"

    @property
    def slides_link(self):
        return self.dst_prefix.replace('\\', '/') + "-slides.pdf"

    @property
    def testimonial_link(self):
        return self.dst_prefix.replace('\\', '/') + "-testimonial.pdf"

    @property
    def review_link(self):
        return self.dst_prefix.replace('\\', '/') + "-testimonial.pdf"

    def process(self):
        if os.path.isfile(os.path.join(self.src_folder, 'text.pdf')):
            shutil.copyfile(os.path.join(self.src_folder, 'text.pdf'), self.text_link)

        if os.path.isfile(os.path.join(self.src_folder, 'slides.pdf')):
            shutil.copyfile(os.path.join(self.src_folder, 'slides.pdf'), self.slides_link)
        else:
            self.has_slides = False

        if os.path.isfile(os.path.join(self.src_folder, 'testimonial.pdf')):
            shutil.copyfile(os.path.join(self.src_folder, 'testimonial.pdf'), self.testimonial_link)
        else:
            self.has_testimonial = False

        if os.path.isfile(os.path.join(self.src_folder, 'review.pdf')):
            shutil.copyfile(os.path.join(self.src_folder, 'review.pdf'), self.review_link)
        else:
            self.has_review = False

        if self.has_code_archive:
            shutil.copyfile(os.path.join(self.src_folder, 'code.' + self.code_type), self.code_link)

    def __str__(self):
        return self.dst_prefix


if __name__=='__main__':
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(__script_dir__))
    try:
        table_template = env.get_template("table.jinja2")
    except jinja2.exceptions.TemplateSyntaxError as te:
        print("Template syntax error:", te, "@", te.lineno, file=sys.stderr)

    titles = {}
    supervisors = {}
    reviewers = {}
    with open('titles.csv', 'r', encoding="utf-8-sig") as csvfile:
        titlereader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        for row in titlereader:
            if row:
                titles[row[0].strip()] = row[1].strip()
                supervisors[row[0].strip()] = row[2].strip()
                reviewers[row[0].strip()] = row[3].strip()

    bakas = []
    for fn in glob.glob('*'):
        if os.path.isdir(fn) and len(os.listdir(fn)) and ' ' in fn:
            bakas.append(Baka(fn, titles[fn], supervisors[fn], reviewers[fn]))
    bakas.sort(key=lambda b: b.fio)

    os.makedirs(Baka.subdir, exist_ok=True)

    with open('out.html', 'w+', encoding="utf-8") as outhtml:
        for b in bakas:
            b.process()

        try:
            print(table_template.render(bakas=bakas), file=outhtml)
        except jinja2.exceptions.TemplateError as te:
            print("Template syntax error:", te, file=sys.stderr)
