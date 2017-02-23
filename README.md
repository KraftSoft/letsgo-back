API
===
Список мероприятий
------------------
<br/><br/>GET /meetings-list/<br/>
**Example request headers:**
`GET /meetings-list/ HTTP/1.1`<br/>
`Accept: */*`<br/>
`Accept-Encoding: gzip, deflate`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Connection: keep-alive`<br/>
`Host: 185.76.147.143`<br/>
`User-Agent: HTTPie/0.9.6`<br/>
<br/>
`http 185.76.147.143/meetings-list/ 'Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2'`

Добавление мероприятия
----------------------
<br/>
POST /meetings-list/<br/>
**Example request headers:**<br/>
`User-Agent: curl/7.35.0`<br/>
`Host: 185.76.147.143`<br/>
`Accept: */*`<br/>
`Content-Type: application/json`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Content-Length: xxx`<br/>
<br/>
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
<br/>
PUT /user-detail/1/<br/>
<br/>
**Example request headers:**<br/>
`User-Agent: curl/7.35.0`<br/>
`Host: 185.76.147.143`<br/>
`Accept: */*`<br/>
`Content-Type: application/json`<br/>
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`<br/>
`Content-Length: 77`<br/>
<br/>
```
{
    "username": "new_nick", 
    "firs_name": "new first name", 
    "about": "new about"
}
```
`curl -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X PUT -d '{"username": "new_nick", "firs_name": "new first name", "about": "new about"}' 185.76.147.143/user-detail/1/`