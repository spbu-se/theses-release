﻿Этот чудо-скрипт понимает следующую структуру подкаталогов в текущем:

```
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
```

* `code.hyperlink` должен содержать единственную строчку со ссылкой.
* `code.txt` — комментарий на случай отсутствия кода, в духе «Код закрыт».

Для метаинформации требуется `titles.csv` со строками вида (`\t` -- табуляция):
`Терехов Андрей Николаевич\tТехнология программирования встроенных систем реального времени`

Требуется параметр — подкаталог для генерации, в который будут сложены файлы и на который будет ссылаться HTML.
