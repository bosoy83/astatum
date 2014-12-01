Astatum
=======

Простой self hosted Pocket/Readability сервис с хранением полного содержимого статьи

![](http://cl.ly/image/2J3A3q3x3f0P/Image%202014-07-18%20at%2010.03.44%20%D0%B4%D0%BE%20%D0%BF%D0%BE%D0%BB%D1%83%D0%B4%D0%BD%D1%8F.png "Главная")

![](http://cl.ly/image/2j1B1u2A3G45/Image%202014-07-18%20at%2010.04.18%20%D0%B4%D0%BE%20%D0%BF%D0%BE%D0%BB%D1%83%D0%B4%D0%BD%D1%8F.png "Лог")

## Установка
```sh
$ mkdir /srv
$ cd /srv
$ git clone https://github.com/x0x01/astatum.git
$ cd astatum
$ chmod 777 static/img
$ pip install -r requirements.txt
Отредактировать config.py
$ python astatum.py
```

## Возможности
- Трансляция полного текста статей в RSS
- Кнопка "В закладки!", позволяющая сохранить открытую в браузере статью
- Загрузка статей из RSS ленты
- Локальное кэширование изображений
- Для выдиления контента используется парсер readability
- Python, Flask, SQLAlchemy, Bootstrap 3

## UseCase
В [TinyTinyRSS](http://tt-rss.org/redmine/projects/tt-rss/wiki) есть собственная RSS лента избанных статей. 
Подключаем ее к Astatum в config.py, выходную RSS ленту Astatum - добавляем в TinyTinyRSS (рекурсия!!!)

Результат: когда в TinyTinyRSS статья отмечается как избранная, полное содержимое этой статьи загружается Astatum, после чего экспортируестя в ленту RSS. Которую, в свою очередь, удобно читать на мобильном устройстве, а упрощенная копия статьи будет доступна даже после удаления оригинальной ссылки (и больше никто не сможет убрать пост в черновики!)
