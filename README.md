
## 1. Описание задания

#### Основные задачи:

- [x] Из сайтов источников требуется собрать данные из любой категории:
        ◦ Ссылка на товар
        ◦ Название товара
        ◦ Цена со скидкой
        ◦ Цена без скидки
        ◦ Остатки
- [x] Количество страниц в категории ограничить до 3.
- [ ] Обработать возможные ошибки и блокировки.
- [x] Реализовать асинхронный подход как к постраничной пагинации, так и к итерации по ссылкам товаров, так же ограничить число одновременных сетевых запросов.
- [x] Данные сохранить в таблицу PostgreSQL.
- [ ] Docker compose.


## 2. Описание сервиса 

Как выглядит сервис

```
flowchart TB
    CookiesLoaders-->UseCases
    Api-Handlers-->UseCases
    Service-AU-->UseCases
    Service-OZ-->UseCases
    Service-WB-->UseCases
    UseCases-->Interface
    Interface-->Repository
```

+ Приложение состоит из нескольких слоев:
    + Repository - слой моделями SqlAlchemy и методами чтения/записи в PostgreSQL. Также качестве хранилища используются файлы куки
    + UseCases - слой с бизнес логикой
    + Services - слой с сервисами. Всего сервисов 4: 
       + парсер WB (Wildberries)
       + парсер OZ (Ozon)
       + парсер AU (Auchan)
       + CookiesLoader - скрипт для загрузки и хранения куков для парсера OZ
    + Api Handkers - слой представления, где располагаются ручки
    + DI Container - контейнер, где инициализируются все зависимости 

## 3. Как запустить

Из докера:

+ git clone git@github.com:iriskin77/test_wb_oz_au_parsers.git
+ docker-compose build
+ docker-compose up

Далее приложение развернется на порту localhost: 8092

Из виртуального окружения:

+ git clone git@github.com:iriskin77/test_wb_oz_au_parsers.git
+ python3 -m venv venv
+ source/venv/bin/activate

