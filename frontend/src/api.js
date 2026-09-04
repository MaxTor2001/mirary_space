/** Тонкий клиент к Django REST API магазина Mirari. */
const API_URL = process.env.API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

/** Разворачивает ошибку DRF в одну читаемую строку. */
function errorMessage(data, status) {
  if (!data) return `Ошибка запроса (${status})`;
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  return Object.entries(data)
    .map(([field, messages]) => `${field}: ${[].concat(messages).join(", ")}`)
    .join("; ");
}

/** Выполняет запрос к API, подставляя токен и ключ анонимной корзины. */
export async function api(path, { method = "GET", body, session } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (session?.token) headers.Authorization = `Token ${session.token}`;
  if (session?.cartSession) headers["X-Cart-Session"] = session.cartSession;

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(errorMessage(data, response.status), response.status, data);
  return data;
}

export { API_URL };
