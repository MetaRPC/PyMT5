---
hide:
  - navigation
  - toc
---

# Документация PyMT5 SDK

> ℹ️ **Account ID / Session ID**: При подключении через `Connect` / `ConnectEx` MetaRPC автоматически генерирует GUID сессии терминала и возвращает его в `terminalInstanceGuid`. Нет необходимости вызывать `GetId` или передавать заголовок `id` перед подключением. Последующие вызовы (такие как подписки или запросы ордеров) используют этот ID сессии автоматически.

<div class="hx-wrap" markdown="0">

<div class="hx-hero">
  <p class="hx-sub">Полноценный Python SDK для автоматизации торговли в MetaTrader 5 через gRPC &amp; REST — подключайтесь, стримьте живые тики и исполняйте сделки из любого Python-приложения.</p>
  <div class="hx-stats">
    <div class="hx-stat"><span class="hx-statV">3</span><span class="hx-statL">слоя API</span></div>
    <div class="hx-stat"><span class="hx-statV">gRPC</span><span class="hx-statL">+ протокол REST</span></div>
    <div class="hx-stat"><span class="hx-statV">MT5</span><span class="hx-statL">облачный терминал</span></div>
    <div class="hx-stat"><span class="hx-statV">Python 3.8+</span><span class="hx-statL">среда выполнения</span></div>
  </div>
</div>

<div class="hx-cards hx-cards-4">

  <a href="All_Guides/Your_First_Project/" class="hx-gc hx-orange">
    <div class="hx-gcTop"></div>
    <div class="hx-gcBody">
      <div class="hx-gcTag">Начало работы</div>
      <div class="hx-gcTitle">Быстрый старт</div>
      <p class="hx-gcDesc">Ваш первый проект с нуля за 10 минут. Подключитесь, прочитайте баланс, разместите сделку.</p>
      <div class="hx-gcCount">10 мин · практика</div>
    </div>
  </a>

  <a href="All_Guides/GETTING_STARTED/" class="hx-gc hx-blue">
    <div class="hx-gcTop"></div>
    <div class="hx-gcBody">
      <div class="hx-gcTag">Изучение</div>
      <div class="hx-gcTitle">Getting Started</div>
      <p class="hx-gcDesc">Впервые здесь? Начните с установки, настройки и обзора того, как организован SDK.</p>
      <div class="hx-gcCount">установка · обзор</div>
    </div>
  </a>

  <a href="All_Guides/PROJECT_MAP/" class="hx-gc hx-purple">
    <div class="hx-gcTop"></div>
    <div class="hx-gcBody">
      <div class="hx-gcTag">Архитектура</div>
      <div class="hx-gcTitle">Project Map</div>
      <p class="hx-gcDesc">Обзор архитектуры — как низкоуровневый, среднеуровневый и sugar-слои сочетаются друг с другом.</p>
      <div class="hx-gcCount">структура · слои</div>
    </div>
  </a>

  <a href="All_Guides/SDK_Ecosystem/" class="hx-gc hx-pink">
    <div class="hx-gcTop"></div>
    <div class="hx-gcBody">
      <div class="hx-gcTag">Экосистема</div>
      <div class="hx-gcTitle">Trade Copier</div>
      <p class="hx-gcDesc">Зеркалируйте стратегию между счетами — как PyMT5 работает в паре с PyCopier (мастер → подписчики).</p>
      <div class="hx-gcCount">копировщик · мастер → подписчики</div>
    </div>
  </a>

</div>

<div class="hx-cards">

  <a href="MT5Account/MT5Account.Master.Overview/" class="hx-gc hx-teal">
    <div class="hx-gcTop"></div>
    <div class="hx-gcBody">
      <div class="hx-gcTag">Справочник · Низкоуровневый</div>
      <div class="hx-gcTitle">MT5Account</div>
      <p class="hx-gcDesc">Прямой слой gRPC / protobuf. Максимальный контроль над каждым запросом и ответом.</p>
      <div class="hx-gcCount">чистый gRPC · полный контроль</div>
    </div>
  </a>

  <a href="MT5Service/MT5Service.Overview/" class="hx-gc hx-rose">
    <div class="hx-gcTop"></div>
    <div class="hx-gcBody">
      <div class="hx-gcTag">Справочник · Среднеуровневый</div>
      <div class="hx-gcTitle">MT5Service</div>
      <p class="hx-gcDesc">Чистая обёртка над MT5Account с нативными типами Python и удобными методами.</p>
      <div class="hx-gcCount">на 30–50% меньше кода</div>
    </div>
  </a>

  <a href="MT5Sugar/MT5Sugar.Master.Overview/" class="hx-gc hx-green">
    <div class="hx-gcTop"></div>
    <div class="hx-gcBody">
      <div class="hx-gcTag">Справочник · Высокоуровневый</div>
      <div class="hx-gcTitle">MT5Sugar</div>
      <p class="hx-gcDesc">Операции в одну строку, расчёт объёма на основе риска и умные значения по умолчанию для быстрых стратегий.</p>
      <div class="hx-gcCount">однострочники · расчёт по риску</div>
    </div>
  </a>

</div>

</div>
