Понял! Вот curl команды для каждой ручки по одной:

## Базовые
```bash
curl http://localhost:8000/
curl http://localhost:8000/users
curl http://localhost:8000/addresses
```

## Пользователи (CRUD)
```bash
curl http://localhost:8000/users/1
curl -X POST http://localhost:8000/users -H "Content-Type: application/json" -d '{"username": "test", "email": "test@test.com", "full_name": "Test User"}'
curl -X PUT http://localhost:8000/users/1 -H "Content-Type: application/json" -d '{"username": "updated", "email": "updated@test.com", "full_name": "Updated User"}'
curl -X DELETE http://localhost:8000/users/1
```

## Адреса (CRUD)
```bash
curl http://localhost:8000/users/1/addresses
curl -X POST http://localhost:8000/addresses -H "Content-Type: application/json" -d '{"user_id": 1, "country": "Russia", "city": "Moscow", "street": "Main", "house_number": "1"}'
curl -X DELETE http://localhost:8000/addresses/1
```

## Поиск пользователей
```bash
curl "http://localhost:8000/users/search/?username=test"
curl "http://localhost:8000/users/search/?email=test.com"
curl "http://localhost:8000/users/search/?full_name=Test"
curl "http://localhost:8000/users/search/?username=test&email=test.com"
curl http://localhost:8000/users/search/1
curl http://localhost:8000/users/search/test
curl http://localhost:8000/users/1/exists
curl http://localhost:8000/users/email/test@test.com/exists
```

Каждая команда тестирует одну конкретную ручку! 🎯