/**
 * Уведомляет Яндекс и Bing об изменившихся страницах по протоколу IndexNow.
 *
 *   node scripts/indexnow.js            # все адреса из sitemap.xml
 *   node scripts/indexnow.js /catalog   # только указанные пути
 *
 * Карта сайта — единственный источник адресов, чтобы второй список не разъехался
 * с первым. Запускается руками после реальных изменений: на потоке лишних
 * уведомлений поисковик начинает их игнорировать.
 */
const SITE_URL = (process.env.SITE_URL || "https://mirari.space").replace(/\/$/, "");
const KEY = process.env.INDEXNOW_KEY;
const ENDPOINT = "https://api.indexnow.org/indexnow";

if (!KEY) {
  console.error("Не задан INDEXNOW_KEY");
  process.exit(1);
}

const paths = process.argv.slice(2);
let urls;
if (paths.length) {
  urls = paths.map((p) => SITE_URL + (p.startsWith("/") ? p : `/${p}`));
} else {
  const xml = await fetch(`${SITE_URL}/sitemap.xml`).then((r) => r.text());
  urls = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map((m) => m[1].replace(/&amp;/g, "&"));
}

const response = await fetch(ENDPOINT, {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify({
    host: new URL(SITE_URL).host,
    key: KEY,
    keyLocation: `${SITE_URL}/${KEY}.txt`,
    urlList: urls,
  }),
});

console.log(`Отправлено адресов: ${urls.length}`);
console.log(`Ответ IndexNow: ${response.status} ${response.statusText}`);
if (response.status === 403) console.log("403 — ключ не совпадает с тем, что отдаётся по keyLocation");
if (response.status === 422) console.log("422 — в списке есть адреса с чужого домена");
