/*
 * Счётчик Яндекс.Метрики. Номер приходит в data-id тега <script>, который этот
 * файл подключает, а сам номер задаётся в .env (YANDEX_METRIKA_ID). Отдельным
 * файлом, а не инлайном, чтобы номер менялся без правки разметки.
 *
 * webvisor: false — запись сессий выключена: на страницах оформления заказа
 * посетитель вводит имя, телефон и адрес, и писать это в запись сессии незачем.
 */
(function () {
    var id = document.currentScript && document.currentScript.dataset.id;
    if (!id) return;
    var src = "https://mc.yandex.ru/metrika/tag.js?id=" + id;

    (function (m, e, t, r, i, k, a) {
        m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
        m[i].l = 1 * new Date();
        for (var j = 0; j < document.scripts.length; j++) { if (document.scripts[j].src === r) { return; } }
        k = e.createElement(t); a = e.getElementsByTagName(t)[0];
        k.async = 1; k.src = r; a.parentNode.insertBefore(k, a);
    })(window, document, "script", src, "ym");

    ym(id, "init", {
        ssr: true,
        clickmap: true,
        trackLinks: true,
        accurateTrackBounce: true,
        webvisor: false
    });
})();
