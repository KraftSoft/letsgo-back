
API
===
Список мероприятий
GET /meetings-list/
<details>
**Request headers:**
`GET /meetings-list/ HTTP/1.1`
`Accept: */*`
`Accept-Encoding: gzip, deflate`
`Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2`
`Connection: keep-alive`
`Host: 185.76.147.143`
`User-Agent: HTTPie/0.9.6`

```python
[
    {
        "coordinates": {
            "lat": 55.739675, 
            "lng": 37.483292
        }, 
        "description": "CAtch", 
        "id": 3, 
        "owner": {
            "about": "", 
            "avatar": null, 
            "first_name": "", 
            "href": "http://185.76.147.143/user-detail/1/", 
            "id": 1, 
            "photos": [
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }
            ], 
            "username": "w3data"
        }, 
        "subway": null, 
        "title": "Catch pokemons together"
    }, 
    {
        "coordinates": {
            "lat": 55.795105, 
            "lng": 37.676239
        }, 
        "description": "d1", 
        "id": 6, 
        "owner": {
            "about": "", 
            "avatar": null, 
            "first_name": "", 
            "href": "http://185.76.147.143/user-detail/2/", 
            "id": 2, 
            "photos": [], 
            "username": "qq"
        }, 
        "subway": null, 
        "title": "t1"
    }, 
    {
        "coordinates": {
            "lat": 55.761702, 
            "lng": 37.624397
        }, 
        "description": "CAtch", 
        "id": 1, 
        "owner": {
            "about": "", 
            "avatar": null, 
            "first_name": "", 
            "href": "http://185.76.147.143/user-detail/1/", 
            "id": 1, 
            "photos": [
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }, 
                {
                    "photo": "/uploads/1.png"
                }
            ], 
            "username": "w3data"
        }, 
        "subway": null, 
        "title": "Catch pokemons together"
    }
]
```
</details>

Добавление мероприятия
POST /meetings-list/
c json 
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
`curl -H "Content-Type: application/json" -H "Authorization: Token 163df7faa712e242f7e6b4d270e29401e604b9b2" -X POST -d '{"title": "title", "description": "desc", "coordinates": {"lat": 20, "lng":30}}'`