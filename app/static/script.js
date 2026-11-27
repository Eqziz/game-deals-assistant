"use strict";

const copy = {
  privacy: ["Конфиденциальность", "Privacy policy"],
  terms: ["Условия использования", "Terms of use"],
  skip: ["К содержанию", "Skip to content"],
  login: ["Войти через Google", "Sign in with Google"],
  logout: ["Выйти", "Sign out"],
  catalog: ["Каталог", "Catalog"],
  favorites: ["Избранное", "Favorites"],
  library: ["Библиотека", "Library"],
  profiles: ["Мои профили", "My profiles"],
  linkProfile: ["Привязать профиль", "Link a profile"],
  platformName: ["Название площадки", "Platform name"],
  profileID: ["Игровой ID, ник или ссылка на профиль", "Player ID, username, or profile URL"],
  profileHint: ["Выберите площадку и сохраните свой игровой ID или публичную ссылку.", "Select a platform and save your player ID or public profile URL."],
  noProfiles: ["Вы пока не добавили игровые профили.", "You haven’t added any gaming profiles yet."],
  editProfile: ["Изменить", "Edit"],
  unlink: ["Отвязать", "Unlink"],
  deals: ["Скидки на игры", "Game deals"],
  close: ["Закрыть", "Dismiss"],
  search: ["Поиск по названию", "Search games by title"],
  store: ["Магазин", "Store"],
  allStores: ["Все магазины", "All stores"],
  filters: ["Фильтры", "Filters"],
  find: ["Найти", "Search"],
  min: ["Скидка от, %", "Min. discount, %"],
  max: ["Скидка до, %", "Max. discount, %"],
  hideOwned: ["Скрыть купленные", "Hide owned games"],
  reset: ["Сбросить", "Reset filters"],
  all: ["Все скидки", "All deals"],
  under5: ["До $5", "Up to $5"],
  free: ["Бесплатно", "Free"],
  sort: ["Сортировка", "Sort"],
  byDiscount: ["По скидке", "Highest discount"],
  low: ["Сначала дешевле", "Lowest price"],
  high: ["Сначала дороже", "Highest price"],
  rating: ["По рейтингу", "Deal rating"],
  byTitle: ["По названию", "Title"],
  byStore: ["По магазину", "Store"],
  more: ["Показать ещё", "Load more"],
  librarySearch: ["Поиск в библиотеке", "Search library"],
  platform: ["Платформа", "Platform"],
  platforms: ["Все платформы", "All platforms"],
  addGame: ["Добавить игру", "Add a game"],
  steamLibrary: ["Библиотека Steam", "Steam library"],
  steamHint: [
    "Введите 17 цифр SteamID64. Откройте доступ к играм в настройках приватности Steam.",
    "Enter your 17-digit SteamID64. Set game details to public in your Steam privacy settings.",
  ],
  import: ["Импортировать", "Import games"],
  game: ["Название игры", "Game title"],
  appId: ["App ID (необязательно)", "App ID (optional)"],
  playtime: ["Сыграно, часов", "Hours played"],
  add: ["Добавить", "Add game"],
  target: ["Желаемая цена", "Target price"],
  targetUSD: ["Желаемая цена, USD", "Target price, USD"],
  cancel: ["Отмена", "Cancel"],
  save: ["Сохранить", "Save"],
  saveFavorite: ["В избранное", "Save favorite"],
  removeFavorite: ["Убрать из избранного", "Remove favorite"],
  remove: ["Удалить", "Remove"],
  open: ["В магазин", "Visit store"],
  guest: [
    "Войдите, чтобы открыть этот раздел.",
    "Sign in to open this section.",
  ],
  busy: ["Загрузка…", "Loading…"],
  failed: ["Не удалось загрузить данные.", "Couldn’t load this data."],
  actionFailed: [
    "Не удалось выполнить действие. Попробуйте ещё раз.",
    "The action failed. Please try again.",
  ],
  retry: ["Повторить", "Try again"],
  emptyDeals: [
    "По этим фильтрам скидок не найдено.",
    "No deals match these filters.",
  ],
  emptyFav: [
    "Здесь появятся игры, которые вы сохраните в каталоге.",
    "Games you save in the catalog will appear here.",
  ],
  emptyLib: ["В библиотеке пока нет игр.", "Your library is empty."],
  noMatch: ["Игры не найдены.", "No matching games."],
  count: ["Предложений", "Deals"],
  owned: ["В библиотеке", "Owned"],
  currentPrice: ["Текущая цена", "Current price"],
  reached: ["Цена достигнута", "Target reached"],
  saved: ["Сохранено", "Saved"],
  removed: ["Удалено", "Removed"],
  imported: ["Импортировано игр", "Games imported"],
  hours: ["ч", "hrs"],
  other: ["Другая", "Other"],
  unavailable: [
    "Вход через Google временно недоступен.",
    "Google sign-in is temporarily unavailable.",
  ],
  authFailed: [
    "Вход не завершён. Попробуйте ещё раз.",
    "Sign-in wasn’t completed. Please try again.",
  ],
  invalidRange: [
    "Минимальная скидка должна быть не больше максимальной.",
    "Minimum discount must be less than or equal to maximum discount.",
  ],
  unavailableDeal: [
    "Предложение больше недоступно.",
    "This deal is no longer available.",
  ],
  session: [
    "Сессия завершена. Войдите снова.",
    "Your session has ended. Please sign in again.",
  ],
  serviceError: [
    "Сервис сейчас недоступен. Попробуйте позже.",
    "Service is currently unavailable. Please try again later.",
  ],
  steamError: [
    "Импорт не удался. Проверьте SteamID64 и доступ к играм в профиле.",
    "Import failed. Check the SteamID64 and the profile’s game privacy settings.",
  ],
  untitled: ["Без названия", "Untitled"],
  lang: ["Switch to English", "Переключить на русский"],
};
const $ = (id) => document.getElementById(id);
const read = (storage, key) => {
  try {
    return storage.getItem(key);
  } catch {
    return null;
  }
};
const write = (storage, key, value) => {
  try {
    if (value === null) storage.removeItem(key);
    else storage.setItem(key, value);
  } catch {
    /* Storage may be disabled. */
  }
};
let language = read(localStorage, "language") === "en" ? "en" : "ru";
const t = (key) => copy[key][language === "ru" ? 0 : 1];
const price = (number) =>
  new Intl.NumberFormat(language, {
    style: "currency",
    currency: "USD",
    currencyDisplay: "narrowSymbol",
  }).format(number);
const platforms = {
  steam: "Steam",
  epic: "Epic Games",
  gog: "GOG",
  ea: "EA",
  ubisoft: "Ubisoft Connect",
  xbox: "Xbox",
  playstation: "PlayStation Network",
  nintendo: "Nintendo Switch",
  battlenet: "Battle.net",
  riot: "Riot Games",
  rockstar: "Rockstar Games",
  itch: "itch.io",
  amazon: "Amazon Games",
  vkplay: "VK Play",
  other: "",
};
const icons = {
  favorite: "M6 3.5h12v17L12 17l-6 3.5z",
  target:
    "M12 3v2m0 14v2M3 12h2m14 0h2M19 12a7 7 0 1 1-14 0 7 7 0 1 1 14 0z M14 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0z",
  remove: "M4 7h16M9 7V4h6v3m-9 0 1 13h10l1-13M10 10v7m4-7v7",
};
function node(tag, cls, content) {
  const element = document.createElement(tag);
  if (cls) element.className = cls;
  if (content != null) element.textContent = content;
  return element;
}
function button(label, callback, icon) {
  const btn = node("button", "", icon ? null : label);
  btn.type = "button";
  btn.addEventListener("click", callback);
  if (icon) {
    btn.title = label;
    btn.setAttribute("aria-label", label);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "1.7");
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS(svg.namespaceURI, "path");
    path.setAttribute("d", icons[icon]);
    svg.append(path);
    btn.append(svg);
  }
  return btn;
}
function safeURL(raw) {
  if (typeof raw !== "string") return null;
  try {
    const url = new URL(raw);
    return ["http:", "https:"].includes(url.protocol) &&
      !url.username &&
      !url.password
      ? url.href
      : null;
  } catch {
    return null;
  }
}
const state = {
  me: null,
  authStatus: "loading",
  tab: "deals",
  deals: [],
  next: null,
  load: "loading",
  append: false,
  preset: "all",
  query: null,
  favorites: [],
  library: [],
  accounts: [],
  favoriteStatus: "idle",
  libraryStatus: "idle",
  accountStatus: "idle",
};
let requestId = 0,
  personalVersion = 0,
  requestController,
  searchTimer,
  toastTimer,
  dialogDeal,
  targetOpener;
const personalRequests = { favorites: 0, library: 0, accounts: 0 };
const personalResources = {
  favorites: ["/api/favorites", "favoriteStatus"],
  library: ["/api/owned-games", "libraryStatus"],
  accounts: ["/api/accounts", "accountStatus"],
};
function message(box, key, action, callback) {
  const div = node("div", "empty");
  div.append(node("p", "", t(key)));
  if (action) div.append(button(t(action), callback));
  box.replaceChildren(div);
}
function toast(key) {
  clearTimeout(toastTimer);
  $("toast").textContent = t(key);
  toastTimer = setTimeout(() => $("toast").replaceChildren(), 3500);
}
function notice(key) {
  $("notice").hidden = !key;
  $("notice").dataset.key = key || "";
  $("notice").querySelector("span").textContent = key ? t(key) : "";
}
async function api(path, method = "GET", body, signal) {
  const response = await fetch(path, {
    method,
    credentials: "same-origin",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
    signal,
    cache: "no-store",
  });
  if (response.status === 401) {
    clearPersonal();
    state.authStatus = "ready";
    renderPersonal();
    renderAccount();
    renderDeals();
    notice("session");
  }
  if (!response.ok) throw new Error(String(response.status));
  return response.status === 204 ? null : response.json();
}
function applyLanguage() {
  document.documentElement.lang = language;
  document
    .querySelectorAll("[data-t]")
    .forEach((el) => (el.textContent = t(el.dataset.t)));
  document
    .querySelectorAll("[data-placeholder]")
    .forEach((el) => (el.placeholder = t(el.dataset.placeholder)));
  $("language").textContent = language === "ru" ? "EN" : "RU";
  $("language").setAttribute("aria-label", t("lang"));
  for (const select of [$("manualPlatform"), $("libraryPlatform"), $("profilePlatform")]) {
    const selected = select.value;
    select.replaceChildren();
    if (select.id === "libraryPlatform")
      select.add(new Option(t("platforms"), ""));
    for (const [value, label] of Object.entries(platforms))
      select.add(new Option(label || t("other"), value));
    if ([...select.options].some((o) => o.value === selected))
      select.value = selected;
  }
  if ($("notice").dataset.key) notice($("notice").dataset.key);
  renderAccount();
  renderDeals();
  renderPersonal();
}
function setTab() {
  if (location.hash === "#sync") history.replaceState(null, "", "#profiles");
  const hash = location.hash.slice(1);
  state.tab = ["favorites", "library", "profiles"].includes(hash) ? hash : "deals";
  document
    .querySelectorAll("main > section")
    .forEach((el) => (el.hidden = el.id !== state.tab));
  document.querySelectorAll("nav a").forEach((a) => {
    if (a.hash === "#" + state.tab) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  document.title = t(state.tab) + " · Game Deals Assistant";
}
function renderAccount() {
  $("account").textContent = t(state.me ? "logout" : "login");
  $("account").disabled = state.authStatus === "loading";
  $("identity").textContent = state.me?.name || state.me?.email || "";
}
function clearPersonal() {
  personalVersion++;
  state.me = null;
  state.favorites = [];
  state.library = [];
  state.accounts = [];
  state.favoriteStatus = state.libraryStatus = state.accountStatus = "idle";
  $("profileRows").replaceChildren();
  $("profileForm").reset();
  updateCustomPlatform();
  state.deals.forEach((d) => {
    d.is_favorite = false;
    d.owned = false;
  });
  $("owned").checked = false;
  if ($("priceDialog").open) $("priceDialog").close();
  $("steamForm").reset();
  $("steamForm").elements.steam_id.defaultValue = "";
  $("steamForm").elements.steam_id.value = "";
  $("manualForm").reset();
  document.querySelectorAll(".feedback").forEach((el) => el.replaceChildren());
}
function login(deal, action) {
  write(
    sessionStorage,
    "returnToDeal",
    JSON.stringify({
      tab: state.tab,
      url: deal?.deal_url,
      title: deal?.title,
      action,
      filters: values(),
      sort: $("sort").value,
      preset: state.preset,
      time: Date.now(),
    }),
  );
  location.assign(
    "/auth/login?" + new URLSearchParams({ next: "/#" + state.tab }),
  );
}
async function identify() {
  try {
    const response = await api("/api/me");
    state.me = response.authenticated ? response.user : null;
    state.authStatus = "ready";
  } catch {
    state.authStatus = "error";
  }
  renderAccount();
  renderPersonal();
}
async function loadPersonal(kind) {
  if (!state.me) return;
  const version = personalVersion;
  const request = ++personalRequests[kind];
  const [path, status] = personalResources[kind];
  state[status] = "loading";
  renderPersonal();
  try {
    const data = await api(path);
    if (version !== personalVersion || request !== personalRequests[kind])
      return;
    state[kind] = data;
    state[status] = "ready";
    if (kind === "accounts") {
      const saved = data.find((account) => account.platform === "steam");
      const steamId = saved?.platform_user_id.match(/^(?:https?:\/\/steamcommunity\.com\/profiles\/)?([0-9]{17})\/?$/i)?.[1] || "";
      const field = $("steamForm").elements.steam_id;
      if (!field.value || field.value === field.defaultValue) field.value = steamId;
      field.defaultValue = steamId;
    }
    if (kind === "favorites") {
      const urls = new Set(data.map((d) => d.deal_url));
      state.deals.forEach((d) => (d.is_favorite = urls.has(d.deal_url)));
    }
  } catch {
    if (version !== personalVersion || request !== personalRequests[kind])
      return;
    state[status] = "error";
  }
  renderPersonal();
  renderDeals();
}
function gate(box) {
  if (state.authStatus === "loading") message(box, "busy");
  else if (state.authStatus === "error")
    message(box, "failed", "retry", bootstrap);
  else message(box, "guest", "login", () => login());
}
function values() {
  return {
    title: $("query").value.trim(),
    store: $("store").value,
    min: $("min").value,
    max: $("max").value,
    owned: $("owned").checked,
  };
}
function validFilters() {
  $("max").setCustomValidity(
    Number($("min").value) > Number($("max").value) ? t("invalidRange") : "",
  );
  if (!$("filters").checkValidity()) {
    setAdvanced(true);
    $("filters").reportValidity();
    return false;
  }
  return true;
}
function setAdvanced(open) {
  $("advanced").hidden = !open;
  $("toggleFilters").setAttribute("aria-expanded", String(open));
}
function showPreset(preset) {
  state.preset = preset;
  document
    .querySelectorAll("[data-preset]")
    .forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.preset === preset)),
    );
}
function queryParams() {
  const v = values();
  const params = new URLSearchParams({
    min_discount: v.min,
    max_discount: v.max,
    page_size: 60,
    hide_owned: String(Boolean(state.me && v.owned)),
  });
  if (v.title) params.set("title", v.title);
  if (v.store === "steam_direct") params.set("source", "steam");
  else if (v.store) params.set("store_id", v.store);
  if (state.preset === "free") params.set("free_only", "true");
  if (state.preset === "under5") params.set("max_price", "5");
  return params;
}
async function loadDeals(append = false) {
  clearTimeout(searchTimer);
  if (append && (state.next == null || state.load === "loading")) return;
  if (!append && !validFilters()) return;
  const token = ++requestId;
  requestController?.abort();
  requestController = new AbortController();
  if (!append) {
    state.deals = [];
    state.next = null;
    state.query = queryParams().toString();
  }
  state.load = "loading";
  state.append = append;
  const params = new URLSearchParams(state.query);
  const page = append ? state.next : 0;
  params.set("page", page);
  renderDeals();
  try {
    const data = await api(
      "/api/deals?" + params,
      "GET",
      undefined,
      requestController.signal,
    );
    if (token !== requestId) return;
    const urls = new Set(state.deals.map((d) => d.deal_url));
    for (const deal of data.deals) {
      if (!deal.deal_url || !urls.has(deal.deal_url)) state.deals.push(deal);
      urls.add(deal.deal_url);
    }
    state.next =
      Number.isInteger(data.next_page) && data.next_page > page
        ? data.next_page
        : null;
    state.load = "ready";
  } catch {
    if (token !== requestId) return;
    state.load = "error";
  }
  renderDeals();
}
function sortedDeals() {
  const sort = $("sort").value;
  const numeric = {
    savings: ["savings", -1],
    low: ["sale_price", 1],
    high: ["sale_price", -1],
    rating: ["deal_rating", -1],
  };
  return [...state.deals].sort((a, b) => {
    if (numeric[sort]) {
      const [key, order] = numeric[sort];
      return order * (Number(a[key] || 0) - Number(b[key] || 0));
    }
    const key = sort === "store" ? "store_name" : "title";
    return String(a[key] || "").localeCompare(String(b[key] || ""), language);
  });
}
function artwork(deal) {
  const cover = node(
    "div",
    "cover",
    (deal.title || "—").slice(0, 1).toUpperCase(),
  );
  cover.setAttribute("aria-hidden", "true");
  const src = safeURL(deal.thumb);
  if (src) {
    const img = node("img");
    img.alt = "";
    img.loading = "lazy";
    img.decoding = "async";
    img.addEventListener(
      "error",
      () => (cover.textContent = (deal.title || "—").slice(0, 1).toUpperCase()),
      { once: true },
    );
    img.src = src;
    cover.replaceChildren(img);
  }
  return cover;
}
function favoriteBody(deal, target) {
  return {
    title: deal.title,
    store_name: deal.store_name,
    deal_url: deal.deal_url,
    sale_price: deal.sale_price,
    normal_price: deal.normal_price,
    savings: deal.savings,
    target_price: target,
  };
}
async function favoriteAction(deal, btn, saved) {
  if (!state.me) {
    login(deal, "favorite");
    return;
  }
  btn.disabled = true;
  try {
    if (saved)
      await api("/api/favorites/delete-by-url", "POST", {
        deal_url: deal.deal_url,
      });
    else await api("/api/favorites", "POST", favoriteBody(deal, null));
    deal.is_favorite = !saved;
    await loadPersonal("favorites");
    toast(saved ? "removed" : "saved");
    focusAction(deal, "favorite");
  } catch {
    if (state.me) toast("actionFailed");
  } finally {
    btn.disabled = false;
  }
}
function target(deal, opener) {
  if (!state.me) {
    login(deal, "target");
    return;
  }
  dialogDeal = deal;
  targetOpener = opener;
  $("targetGame").textContent = deal.title;
  $("currentPrice").textContent =
    t("currentPrice") + " · " + price(deal.sale_price);
  const existing = state.favorites.find((f) => f.deal_url === deal.deal_url);
  $("targetPrice").value = Number(
    existing?.target_price ?? Math.max(0, Number(deal.sale_price) * 0.8),
  ).toFixed(2);
  $("priceForm").querySelector(".feedback").replaceChildren();
  $("priceDialog").showModal();
  $("targetPrice").focus();
  $("targetPrice").select();
}
function dealRow(deal, favorite = false) {
  const row = node("article", "row" + (favorite ? " compact" : ""));
  row.dataset.url = deal.deal_url || "";
  if (!favorite) row.append(artwork(deal));
  const info = node("div");
  info.append(node("h3", "", deal.title || t("untitled")));
  const meta = [deal.store_name];
  if (deal.owned) meta.push(t("owned"));
  if (Number(deal.steam_rating_percent) > 0)
    meta.push("Steam " + deal.steam_rating_percent + "%");
  if (Number(deal.metacritic_score) > 0)
    meta.push("Metacritic " + deal.metacritic_score);
  info.append(node("p", "meta", meta.filter(Boolean).join(" · ")));
  if (favorite && deal.target_price != null)
    info.append(
      node(
        "p",
        "target-info",
        t(
          Number(deal.sale_price) <= Number(deal.target_price)
            ? "reached"
            : "target",
        ) +
          " · " +
          price(deal.target_price),
      ),
    );
  const prices = node("div", "price");
  if (Number(deal.savings) > 0)
    prices.append(
      node("span", "discount", "−" + Math.round(deal.savings) + "%"),
    );
  if (Number(deal.normal_price) > Number(deal.sale_price))
    prices.append(node("del", "", price(deal.normal_price)));
  prices.append(
    node(
      "strong",
      "",
      Number(deal.sale_price) === 0 ? t("free") : price(deal.sale_price),
    ),
  );
  const actions = node("div", "actions"),
    url = safeURL(deal.deal_url);
  if (url) {
    const link = node("a", "button", t("open"));
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    actions.append(link);
    const saved =
      favorite ||
      (state.me &&
        (deal.is_favorite ||
          state.favorites.some((f) => f.deal_url === deal.deal_url)));
    const fav = button(
      t(saved ? "removeFavorite" : "saveFavorite") + " · " + deal.title,
      () => favoriteAction(deal, fav, saved),
      "favorite",
    );
    fav.dataset.action = "favorite";
    fav.setAttribute("aria-pressed", String(Boolean(saved)));
    const alert = button(
      t("target") + " · " + deal.title,
      () => target(deal, alert),
      "target",
    );
    alert.dataset.action = "target";
    actions.append(fav, alert);
  } else if (favorite) {
    const remove = button(
      t("removeFavorite"),
      () => removeRecord("favorites", deal.id, remove),
      "remove",
    );
    actions.append(remove);
  }
  row.append(info, prices, actions);
  return row;
}
function renderDeals() {
  $("count").textContent =
    state.load === "loading" && !state.append
      ? t("busy")
      : state.load === "error" && !state.deals.length
        ? ""
        : t("count") + " · " + state.deals.length;
  $("dealRows").replaceChildren(...sortedDeals().map((d) => dealRow(d)));
  const box = $("dealStatus");
  box.replaceChildren();
  if (state.load === "loading" && state.append) message(box, "busy");
  else if (state.load === "error")
    message(box, "failed", "retry", () => loadDeals(state.append));
  else if (state.load === "ready" && !state.deals.length)
    message(box, "emptyDeals", "reset", resetFilters);
  $("more").hidden = state.next == null || state.load !== "ready";
}
async function removeRecord(kind, id, btn) {
  btn.disabled = true;
  try {
    const path = kind === "favorites" ? "/api/favorites/" : "/api/owned-games/";
    await api(path + encodeURIComponent(id), "DELETE");
    await loadPersonal(kind);
    if (kind === "library") await loadDeals();
    toast("removed");
  } catch {
    if (state.me) toast("actionFailed");
  } finally {
    btn.disabled = false;
  }
}
function updateCustomPlatform() {
  const custom = $("profilePlatform").value === "other";
  $("customPlatformLabel").hidden = !custom;
  const input = $("profileForm").elements.customPlatform;
  input.disabled = !custom;
  input.required = custom;
}

function openManualForm() {
  location.hash = "profiles";
  setTab();
  $("manualForm").elements.title.focus();
}

function editProfile(account) {
  const form = $("profileForm");
  const known = Object.hasOwn(platforms, account.platform) && account.platform !== "other";
  form.elements.platform.value = known ? account.platform : "other";
  updateCustomPlatform();
  form.elements.customPlatform.value = known ? "" : account.platform;
  form.elements.identifier.value = account.platform_user_id;
  form.elements.identifier.focus();
}

async function unlinkProfile(account, control) {
  control.disabled = true;
  try {
    await api("/api/accounts/" + account.id, "DELETE");
    await loadPersonal("accounts");
    toast("removed");
  } catch {
    if (state.me) toast("actionFailed");
  } finally {
    control.disabled = false;
  }
}

function renderProfiles() {
  const box = $("profileRows");
  if (state.accountStatus === "error") {
    message(box, "failed", "retry", () => loadPersonal("accounts"));
    return;
  }
  if (state.accountStatus !== "ready" || !state.accounts.length) {
    message(box, state.accountStatus === "ready" ? "noProfiles" : "busy");
    return;
  }
  box.replaceChildren(...state.accounts.map((account) => {
    const row = node("article", "row compact");
    const info = node("div");
    const label = Object.hasOwn(platforms, account.platform) && platforms[account.platform];
    info.append(node("h3", "", label || account.platform));
    const url = safeURL(account.platform_user_id);
    const identifier = node(url ? "a" : "p", "meta", account.platform_user_id);
    if (url) {
      identifier.href = url;
      identifier.target = "_blank";
      identifier.rel = "noopener noreferrer";
    }
    info.append(identifier);
    const actions = node("div", "actions");
    const unlink = button(t("unlink"), () => unlinkProfile(account, unlink));
    actions.append(button(t("editProfile"), () => editProfile(account)), unlink);
    row.append(info, actions);
    return row;
  }));
}

function renderPersonal() {
  document
    .querySelectorAll(".personal")
    .forEach((el) => (el.hidden = !state.me));
  if (!state.me) {
    for (const id of ["favoriteRows", "libraryRows", "syncGate"]) gate($(id));
    return;
  }
  $("syncGate").replaceChildren();
  renderProfiles();
  for (const [kind, id, status] of [
    ["favorites", "favoriteRows", state.favoriteStatus],
    ["library", "libraryRows", state.libraryStatus],
  ]) {
    const box = $(id);
    if (status === "loading" || status === "idle") {
      message(box, "busy");
      continue;
    }
    if (status === "error") {
      message(box, "failed", "retry", () => loadPersonal(kind));
      continue;
    }
    if (kind === "favorites") {
      if (state.favorites.length)
        box.replaceChildren(...state.favorites.map((d) => dealRow(d, true)));
      else message(box, "emptyFav", "catalog", () => (location.hash = "deals"));
    } else {
      const platform = $("libraryPlatform").value;
      const title = $("librarySearch").value.trim().toLocaleLowerCase();
      const games = state.library.filter(
        (g) =>
          (!platform || g.platform === platform) &&
          (!title || String(g.title).toLocaleLowerCase().includes(title)),
      );
      if (!games.length) {
        if (state.library.length) message(box, "noMatch");
        else
          message(box, "emptyLib", "addGame", openManualForm);
        continue;
      }
      box.replaceChildren(
        ...games.map((game) => {
          const row = node("article", "row compact"),
            info = node("div");
          info.append(
            node("h3", "", game.title),
            node(
              "p",
              "meta",
              [
                platforms[game.platform] ||
                  (game.platform === "other" ? t("other") : game.platform),
                game.platform_game_id,
              ]
                .filter(Boolean)
                .join(" · "),
            ),
          );
          const hours = Number(game.playtime_minutes) / 60;
          const actions = node("div", "actions");
          const btn = button(
            t("remove") + " · " + game.title,
            () => removeRecord("library", game.id, btn),
            "remove",
          );
          actions.append(btn);
          row.append(
            info,
            node(
              "span",
              "meta",
              hours
                ? hours.toLocaleString(language, { maximumFractionDigits: 1 }) +
                    " " +
                    t("hours")
                : "",
            ),
            actions,
          );
          return row;
        }),
      );
    }
  }
}
function resetFilters() {
  $("filters").reset();
  $("max").setCustomValidity("");
  $("sort").value = "savings";
  showPreset("all");
  loadDeals();
}
function focusAction(deal, action) {
  const rows = $(
    state.tab === "favorites" ? "favoriteRows" : "dealRows",
  ).children;
  const row = [...rows].find((r) => r.dataset.url === deal.deal_url);
  const btn = row?.querySelector('[data-action="' + action + '"]');
  btn?.focus();
  return btn;
}

async function loadStores() {
  try {
    const data = await api("/api/stores");
    for (const s of data.all) {
      const id = String(s.store_id);
      if (
        id !== "cheapshark_all" &&
        ![...$("store").options].some((o) => o.value === id)
      ) {
        $("store").add(new Option(s.store_name, id));
      }
    }
  } catch {
    /* Search remains available with the built-in sources. */
  }
}
function resumeLogin() {
  let pending;
  try {
    pending = JSON.parse(read(sessionStorage, "returnToDeal"));
  } catch {
    return null;
  }
  write(sessionStorage, "returnToDeal", null);
  if (!pending || Date.now() - pending.time > 1800000) return null;
  if (pending.filters) {
    const v = pending.filters;
    $("query").value = v.title || "";
    $("min").value = v.min ?? 10;
    $("max").value = v.max ?? 100;
    if (v.store && ![...$("store").options].some((o) => o.value === v.store))
      $("store").add(new Option(v.store, v.store));
    $("store").value = v.store || "";
    $("owned").checked = Boolean(v.owned && state.me);
    $("sort").value = pending.sort || "savings";
    showPreset(pending.preset);
  }
  if (["deals", "favorites", "library", "profiles", "sync"].includes(pending.tab))
    location.hash = pending.tab;
  setTab();
  return pending;
}
async function bootstrap() {
  const stores = loadStores();
  await identify();
  const pending = resumeLogin();
  await Promise.all([
    loadDeals(),
    state.me && loadPersonal("favorites"),
    state.me && loadPersonal("library"),
    state.me && loadPersonal("accounts"),
  ]);
  if (pending?.url && state.me) {
    let deal = state.deals.find((d) => d.deal_url === pending.url);
    if (!deal && pending.title && state.load === "ready") {
      $("query").value = pending.title;
      await loadDeals();
      deal = state.deals.find((d) => d.deal_url === pending.url);
    }
    if (deal) {
      const btn = focusAction(deal, pending.action);
      if (pending.action === "target" && btn) target(deal, btn);
    } else if (state.load === "ready") notice("unavailableDeal");
  }
  await stores;
}
async function accountAction() {
  if (!state.me) {
    login();
    return;
  }
  $("account").disabled = true;
  try {
    await api("/auth/logout", "POST");
    clearPersonal();
    renderPersonal();
    renderAccount();
    await loadDeals();
  } catch {
    toast("actionFailed");
  } finally {
    renderAccount();
  }
}
function bindForm(id, path, payload, onSuccess) {
  const form = $(id);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!state.me) {
      login();
      return;
    }
    const data = new FormData(form);
    const btn = form.querySelector("button.primary"),
      feedback = form.querySelector(".feedback");
    btn.disabled = true;
    feedback.classList.remove("error");
    feedback.textContent = t("busy");
    try {
      const result = await api(path, "POST", payload(data));
      onSuccess(result, feedback);
      form.reset();
      await Promise.all([loadPersonal("library"), loadDeals()]);
    } catch {
      feedback.classList.add("error");
      feedback.textContent = t(
        id === "steamForm" ? "steamError" : "actionFailed",
      );
    } finally {
      btn.disabled = false;
    }
  });
}
$("profilePlatform").addEventListener("change", () => {
  updateCustomPlatform();
  const current = state.accounts.find((a) => a.platform === $("profilePlatform").value);
  $("profileForm").elements.identifier.value = current?.platform_user_id || "";
});
$("openManual").addEventListener("click", openManualForm);
$("profileForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const platform = form.elements.platform.value;
  const control = form.querySelector("button.primary");
  const feedback = form.querySelector(".feedback");
  if (!state.me) return login();
  control.disabled = true;
  feedback.textContent = t("busy");
  try {
    await api("/api/accounts", "PUT", {
      platform: platform === "other" ? form.elements.customPlatform.value.trim() : platform,
      platform_user_id: form.elements.identifier.value.trim(),
    });
    await loadPersonal("accounts");
    feedback.textContent = t("saved");
  } catch {
    if (state.me) feedback.textContent = t("actionFailed");
  } finally {
    control.disabled = false;
  }
});
$("account").addEventListener("click", accountAction);
$("language").addEventListener("click", () => {
  language = language === "ru" ? "en" : "ru";
  write(localStorage, "language", language);
  applyLanguage();
  setTab();
});
$("notice")
  .querySelector("button")
  .addEventListener("click", () => notice(null));
$("filters").addEventListener("submit", (e) => {
  e.preventDefault();
  loadDeals();
});
$("filters").addEventListener("input", () => $("max").setCustomValidity(""));
$("query").addEventListener("input", () => {
  requestController?.abort();
  requestId++;
  state.next = null;
  state.deals = [];
  state.load = "loading";
  renderDeals();
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadDeals(), 300);
});
$("toggleFilters").addEventListener("click", () =>
  setAdvanced($("advanced").hidden),
);
$("reset").addEventListener("click", resetFilters);
$("more").addEventListener("click", () => loadDeals(true));
$("sort").addEventListener("change", renderDeals);
$("store").addEventListener("change", () => loadDeals());
$("owned").addEventListener("change", () => {
  if (!state.me && $("owned").checked) {
    login();
    return;
  }
  loadDeals();
});
for (const el of [$("min"), $("max")])
  el.addEventListener("input", () => showPreset(""));
document.querySelectorAll("[data-preset]").forEach((btn) =>
  btn.addEventListener("click", () => {
    const preset = btn.dataset.preset;
    showPreset(preset);
    $("min").value =
      preset === "free" ? 0 : ["75", "90"].includes(preset) ? preset : 10;
    $("max").value = 100;
    loadDeals();
  }),
);
$("librarySearch").addEventListener("input", renderPersonal);
$("libraryPlatform").addEventListener("change", renderPersonal);
$("cancel").addEventListener("click", () => $("priceDialog").close());
$("priceDialog").addEventListener("close", () => {
  if (targetOpener?.isConnected) targetOpener.focus();
  else if (dialogDeal) focusAction(dialogDeal, "target");
});
$("priceForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = $("priceForm").querySelector("button.primary");
  btn.disabled = true;
  try {
    await api(
      "/api/favorites",
      "POST",
      favoriteBody(dialogDeal, Number($("targetPrice").value)),
    );
    await loadPersonal("favorites");
    $("priceDialog").close();
    toast("saved");
  } catch {
    $("priceForm").querySelector(".feedback").textContent = t("actionFailed");
  } finally {
    btn.disabled = false;
  }
});
bindForm(
  "steamForm",
  "/api/steam/sync",
  (d) => ({ steam_id: d.get("steam_id").trim() }),
  (result, feedback) => {
    feedback.textContent = t("imported") + " · " + result.games_count;
    loadPersonal("accounts");
  },
);
bindForm(
  "manualForm",
  "/api/owned-games/manual",
  (d) => ({
    title: d.get("title").trim(),
    platform: d.get("platform"),
    platform_game_id: d.get("platform_game_id").trim() || null,
    playtime_minutes: Math.round(Number(d.get("hours")) * 60),
  }),
  (result, feedback) => {
    feedback.textContent = t("saved");
  },
);
window.addEventListener("hashchange", setTab);
applyLanguage();
setTab();
const address = new URL(location.href);
if (address.searchParams.has("auth_error")) {
  notice(
    address.searchParams.get("auth_error") === "unavailable"
      ? "unavailable"
      : "authFailed",
  );
  address.searchParams.delete("auth_error");
  history.replaceState(null, "", address);
}
bootstrap();
