# Decken Bot

### Описание
Данный telegram-бот создавался для компнаии **Decken** для внесения планируемых монтажей и и деталей заказа в google-таблицу.


### Подготовка
Для запуска бота и работой над ним необходимо:
* добавить в папку */app* файл БД (пока бот работает только с локальной бд)
* добавить *api* ключи [*telegram*](https://t.me/BotFather) и [*google_api*](https://console.cloud.google.com/)
* добавить в папку */app* файл *service_account* (также получается [отсюда](https://console.cloud.google.com/))


### Запуск
Для запуска необходимо собрать и запустить образ ***Docker***\
Для этого переходим в папку */app* и пишем:\
```
docker build -t decken-bot . && docker run decken-bot
```
