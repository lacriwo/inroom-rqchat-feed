# InRoom RQChat feed

Автообновляемый XML-фид для товарного справочника RQChat.

- Источник: `https://in-room.ru/marketplace/4675585.xml`
- Посадочная страница всех предложений: `https://in-room.rqch.ru/`
- Готовый XML: `https://lacriwo.github.io/inroom-rqchat-feed/inroom-rqchat.xml`
- Обновление: каждые 3 часа через GitHub Actions и вручную через `workflow_dispatch`.

Преобразователь сохраняет исходные данные предложений, заменяет `<url>` и добавляет плоские поля `model`, `color`, `width`, `length`, `lift`, `available_value`, которые можно сопоставлять в RQChat.

