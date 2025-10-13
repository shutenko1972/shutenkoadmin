<!-- Начало

Swagger UI и Админ-панель / shutenkoadmin

Инструкции:
1. Запуск:
python app.py

Узнать структуру приложения:
    cd C:\Users\shute\development\shutenkoadmin
    tree /F

Docker Desktop

 1. Создать образ и запустить контейнер (первый раз)
# Сборка образа
docker build -t shutenkoadmin-app .
# Запуск контейнера с правильным хостом
docker run -d -p 5000:5000 --name shutenkoadmin-container shutenkoadmin-app python -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=True)"

## 2. Просто запустить существующий образ
# Если образ уже собран, просто запускаем
docker run -d -p 5000:5000 --name shutenkoadmin-container shutenkoadmin-app python -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=True)"

## 3. Пересобрать и запустить (при изменениях в коде)
# Останавливаем и удаляем старый контейнер
docker stop shutenkoadmin-container
docker rm shutenkoadmin-container
# Пересобираем образ
docker build -t shutenkoadmin-app .
# Запускаем новый контейнер
docker run -d -p 5000:5000 --name shutenkoadmin-container shutenkoadmin-app python -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=True)"

## 4. Проверка работы
# Проверить статус контейнера
docker ps
# Посмотреть логи
docker logs shutenkoadmin-container

## 5. Если порт 5000 занят
# Использовать порт 5001
docker run -d -p 5001:5000 --name shutenkoadmin-container shutenkoadmin-app python -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=True)"

## 6. Остановка и удаление
# Остановить контейнер
docker stop shutenkoadmin-container
# Удалить контейнер
docker rm shutenkoadmin-container
# Удалить образ (если нужно)
docker rmi shutenkoadmin-app

Приложение доступно по адресу: http://localhost:5000/

Конец -->