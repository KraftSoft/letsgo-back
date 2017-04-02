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
`Host: 37.46.128.134`<br/>
`User-Agent: HTTPie/0.9.6`<br/>

http 37.46.128.134/meetings-list/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Добавление мероприятия
-----------------------
`POST /meetings-list/`<br/>
*Example request headers:*
`User-Agent: curl/7.35.0`<br/>
`Host: 37.46.128.134`<br/>
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
`curl 37.46.128.134/meetings-list/ -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X POST -d '{"title": "title", "description": "desc", "coordinates": {"lat": 20, "lng":30}}'`


Создание пользователя
---------------------
`POST /api-token-auth/ HTTP/1.1`<br/>
*Example request headers:*<br/>
`Host: 37.46.128.134`<br/>
`User-Agent: curl/7.51.0`<br/>
`Accept: */*`<br/>
`Content-Type: application/json`<br/>
`Content-Length: 91`<br/>
```
{
    "social_slug": "vk", 
    "external_id": 112002, 
    "token": "DJSKJDKSA", 
    "first_name": "Ilia228"
}
```

В ответ возвращается токен пользователя, который
можно использовать для следующий запросов, и ссылка
на созданный профиль пользователя

```
{
    "token":"09c6fc397cc3cf22b7056da065ee9d48fbacd680",
    "href":"http://37.46.128.134/user-detail/4/"
}
```

Изменение юзера
----------------
`PUT /user-detail/1/`<br/>
*Example request headers:*
`User-Agent: curl/7.35.0`<br/>
`Host: 37.46.128.134`<br/>
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

`curl -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X PUT -d '{"username": "new_nick", "firs_name": "new first name", "about": "new about"}' 37.46.128.134/user-detail/1/`


Загрузка фото
-------------

http -f PUT 37.46.128.134/upload-photo/55.jpg  <  ~/Downloads/55.jpg 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'

`PUT /upload-photo/55.jpg HTTP/1.1`<br/>
`Accept: */*`<br/>
`Accept-Encoding: gzip, deflate`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Connection: keep-alive`<br/>
`Content-Length: 27475`<br/>
`Content-Type: application/x-www-form-urlencoded; charset=utf-8`<br/>
`Host: 37.46.128.134`<br/>
`User-Agent: HTTPie/0.9.8`<br/>

*в теле запроса бинарные данные картинки*


Установка аватарки
-------------------
http PUT http://37.46.128.134/set-avatar/20/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Удаление фото
-------------------
http DELETE http://37.46.128.134/delete-photo/20/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Список откликов на события текущего юзера
-----------------------------------------
http http://37.46.128.134/confirms-list/   'Authorization: Token ee6d9b6dcdb03b6d7666c4cc14be644272e8c150'

Отправить запрос на участие в событии
-------------------------------------
http POST http://37.46.128.134/meeting-confirm/<meeting_id>/   'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'


Отклонить запрос на участие
---------------------------
http PUT http://37.46.128.134/confirm-action/<confirm_id>/   'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'

is_rejected=True

Принять участника
-------------------
http PUT http://37.46.128.134/confirm-action/<confirm_id>/   'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'
is_approved=True


Редактирование профиля
----------------------
curl 37.46.128.134/user-detail/1/ -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X PUT -d '{"username": "new_nick", "firs_name": "new first name", "about": "new about"}'
