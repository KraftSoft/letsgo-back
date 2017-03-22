API
====
Список мероприятий
--------------------
`GET /meetings-list/`<br/>
*Example request headers:*
`GET /meetings-list/ HTTP/1.1`<br/>
`Accept: */*`<br/>
`Accept-Encoding: gzip, deflate`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Connection: keep-alive`<br/>
`Host: 185.76.147.143`<br/>
`User-Agent: HTTPie/0.9.6`<br/>

http 185.76.147.143/meetings-list/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Добавление мероприятия
-----------------------
`POST /meetings-list/`<br/>
*Example request headers:*
`User-Agent: curl/7.35.0`<br/>
`Host: 185.76.147.143`<br/>
`Accept: */*`<br/>
`Content-Type: application/json`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Content-Length: xxx`<br/>

```
{
    "title": "title",
    "description": "desc",
    "coordinates": {
        "lat": 20,
        "lng":30
    }
}
```
`curl 185.76.147.143/meetings-list/ -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X POST -d '{"title": "title", "description": "desc", "coordinates": {"lat": 20, "lng":30}}'`

Изменение юзера
----------------
`PUT /user-detail/1/`<br/>
*Example request headers:*
`User-Agent: curl/7.35.0`<br/>
`Host: 185.76.147.143`<br/>
`Accept: */*`<br/>
`Content-Type: application/json`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Content-Length: 77`<br/>

```
{
    "username": "new_nick",
    "firs_name": "new first name",
    "about": "new about"
}
```

`curl -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X PUT -d '{"username": "new_nick", "firs_name": "new first name", "about": "new about"}' 185.76.147.143/user-detail/1/`


Загрузка фото
-------------

http -f PUT 185.76.147.143/upload-photo/55.jpg  <  ~/Downloads/55.jpg 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'

`PUT /upload-photo/55.jpg HTTP/1.1`<br/>
`Accept: */*`<br/>
`Accept-Encoding: gzip, deflate`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Connection: keep-alive`<br/>
`Content-Length: 27475`<br/>
`Content-Type: application/x-www-form-urlencoded; charset=utf-8`<br/>
`Host: 185.76.147.143`<br/>
`User-Agent: HTTPie/0.9.8`<br/>

*в теле запроса бинарные данные картинки*


Установка аватарки
-------------------
http PUT http://185.76.147.143/set-avatar/20/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Удаление фото
-------------------
http DELETE http://185.76.147.143/delete-photo/20/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Список откликов на события текущего юзера
-----------------------------------------
http http://185.76.147.143/confirms-list/   'Authorization: Token ee6d9b6dcdb03b6d7666c4cc14be644272e8c150'

Отправить запрос на участие в событии
-------------------------------------
http POST http://185.76.147.143/meeting-confirm/<meeting_id>/   'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Отклонить запрос на участие
---------------------------
http PUT http://185.76.147.143/confirm-action/<confirm_id>/   'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'

is_rejected=True

Принять участника
-------------------
http PUT http://185.76.147.143/confirm-action/<confirm_id>/   'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'
is_approved=True


Редактирование профиля
----------------------
curl 185.76.147.143/user-detail/1/ -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X PUT -d '{"username": "new_nick", "firs_name": "new first name", "about": "new about"}'
