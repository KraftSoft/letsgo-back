API
===
Список мероприятий
------------------
GET /meetings-list/__
**Example request headers:**
`GET /meetings-list/ HTTP/1.1`__
`Accept: */*`
`Accept-Encoding: gzip, deflate`
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`
`Connection: keep-alive`
`Host: 185.76.147.143`
`User-Agent: HTTPie/0.9.6`

`http 185.76.147.143/meetings-list/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'`

Добавление мероприятия
----------------------
POST /meetings-list/
**Example request headers:**
`User-Agent: curl/7.35.0`
`Host: 185.76.147.143`
`Accept: */*`
`Content-Type: application/json`
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`
`Content-Length: xxx`

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
`curl -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X POST -d '{"title": "title", "description": "desc", "coordinates": {"lat": 20, "lng":30}}' 185.76.147.143/meetings-list/`

Изменение юзера
---------------
PUT /user-detail/1/

**Example request headers:**
`User-Agent: curl/7.35.0`
`Host: 185.76.147.143`
`Accept: */*`
`Content-Type: application/json`
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`
`Content-Length: 77`

```
{
    "username": "new_nick", 
    "firs_name": "new first name", 
    "about": "new about"
}
```
`curl -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X PUT -d '{"username": "new_nick", "firs_name": "new first name", "about": "new about"}' 185.76.147.143/user-detail/1/`