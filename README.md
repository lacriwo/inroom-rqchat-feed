# InRoom RQChat feed

Автообновляемый XML-фид для товарного справочника RQChat.

- Источник: `https://in-room.ru/marketplace/4675585.xml`
- Посадочная страница всех предложений: `https://in-room.rqch.ru/`
- Готовый XML: `https://lacriwo.github.io/inroom-rqchat-feed/inroom-rqchat.xml`
- Обновление: один раз в сутки в 00:00 UTC (03:00 по Москве, 06:00 по Омску) через GitHub Actions и вручную через `workflow_dispatch`.

Преобразователь сохраняет основные данные предложений, заменяет `<url>` и добавляет плоские поля `model`, `color`, `width`, `length`, `lift`, `available_value`, которые можно сопоставлять в RQChat. Исходные повторяющиеся узлы `<param>` удаляются из конечного XML, чтобы импортёр RQChat не объединял их в одно поле.

