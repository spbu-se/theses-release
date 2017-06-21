#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# pip install transliterate
from transliterate import translit

import glob
import os
import sys
import shutil
import csv

'''
Этот чудо-скрипт понимает следующую структуру подкаталогов в текущем:

Луцив Дмитирй Вадимович
  L text.pdf
  L slides.pdf
  L code.zip
Кириленко Яков Александрович
  L text.pdf
  L slides.pdf
  L code.7z
Полозов Виктор сергеевич
  L text.pdf
  L slides.pdf
  L code.hyperlink
Сартасов Станислав Юрьевич
  L text.pdf
  L slides.pdf
  L code.txt

code.hyperlink должен содержать единственную строчку со ссылкой

code.txt -- комментарий на случай отсутствия кода, в духе "Код закрыт"

+ titles.csv со строками вида (\t -- табуляция):
Терехов Андрей Николаевич\tТехнология программирования встроенных систем реального времени

Требуется параметр -- подкаталог для генерации, в который будут сложены файлы и на который будет ссылаться HTML.
'''

def dummymd(dirname):
    try:
        os.makedirs(dirname)
    except:
        pass

class Baka:
    subdir = sys.argv[1]
    evenrow = True

    def __init__(self, src_folder, title):
        self.title = title
        self.fio = src_folder
        self.src_folder = src_folder
        self.dst_prefix = os.path.join(Baka.subdir, translit(src_folder, 'ru', reversed=True).replace(' ', '_').replace("'","y"))

    def getHTML(self):
        Baka.evenrow = not Baka.evenrow
        return '<tr class="%s"><td>%s</td><td>%s</td><td><a href="%s">Текст</a></td><td><a href="%s">Презентация</a></td><td>%s</td></tr>' % (
        "even" if Baka.evenrow else "odd",
        self.fio, self.title,
        self.getTextLink(), self.getSlidesLink(),
        self.getCodeComment() if self.hasCodeComment() else ('<a href="%s">Код</a>' % (self.getCodeLink(),) if self.getCodeType() else '')
        )

    def hasCodeArchive(self):
        codeType = self.getCodeType()
        return (codeType in ['zip', '7z'])

    def getCodeType(self):
        "stops after first matching, even if there are multiple"
        for arname in glob.glob(os.path.join(self.src_folder, 'code.*')):
            if arname.endswith('.zip'):
                return 'zip'
            elif arname.endswith('.7z'):
                return '7z'
            elif  arname.endswith('.hyperlink'):
                return 'hyperlink'
            elif  arname.endswith('.txt'):
                return 'txt'
        return None

    def hasCodeLink(self):
        return self.getCodeType() == 'hyperlink'

    def hasCodeComment(self):
        return self.getCodeType() == 'txt'

    def getCodeComment(self):
        if not self.hasCodeComment():
            return None
        else:
            with open(os.path.join(self.src_folder, 'code.txt'), encoding='utf-8') as ccf:
                return ccf.readline().strip()

    def getCodeLink(self):
        if self.hasCodeLink():
            with open(os.path.join(self.src_folder, 'code.hyperlink')) as hlf:
                return hlf.readline().strip()
        elif self.hasCodeArchive():
            return self.dst_prefix.replace('\\', '/') + "-code." + self.getCodeType()

    def getTextLink(self):
        return self.dst_prefix.replace('\\', '/') + "-text.pdf"

    def getSlidesLink(self):
        return self.dst_prefix.replace('\\', '/') + "-slides.pdf"

    def process(self):
        if os.path.isfile(os.path.join(self.src_folder, 'text.pdf')):
            shutil.copyfile(os.path.join(self.src_folder, 'text.pdf'), self.getTextLink())

        if os.path.isfile(os.path.join(self.src_folder, 'slides.pdf')):
            shutil.copyfile(os.path.join(self.src_folder, 'slides.pdf'), self.getSlidesLink())

        if self.hasCodeArchive():
            shutil.copyfile(os.path.join(self.src_folder, 'code.' + self.getCodeType()), self.getCodeLink())

    def __str__(self):
        return self.dst_prefix

titles = {}
with open('titles.csv', 'r', encoding="utf-8-sig") as csvfile:
    titlereader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    for row in titlereader:
        if row:
            titles[row[0].strip()] = row[1].strip()

# print(repr(titles))

bakas = []
for fn in glob.glob('*'):
    if os.path.isdir(fn) and len(os.listdir(fn)) and ' ' in fn:
        bakas.append(Baka(fn, titles[fn]))
bakas.sort(key=lambda b: b.fio)

dummymd(Baka.subdir)

with open('out.html', 'w+', encoding="utf-8") as outhtml:
    print('''<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head>
<body>
<table class="listing">
<thead>
<tr class="odd">
<th>Выпускник</th>
<th>Тема</th>
<th colspan="3">Материалы</th>
</tr>
</thead>
<tbody>''', file=outhtml)
    for b in bakas:
        b.process()
        print(b.getHTML(), file=outhtml)
    print('''</tbody></table>
</body></html>''', file=outhtml)
