let currentLanguage = localStorage.getItem("language") || "ru";

const translations = {
    ru: {
        badge: "Personal Game Deals Assistant",
        mainTitle: "Game Deals Assistant",
        subtitle: "Скидки, избранное, моя библиотека и отметка уже купленных игр.",

        supportTitle: "Поддержать автора",
        supportText: "Если проект оказался полезным, можешь поддержать развитие.",
        supportButton: "Показать реквизиты",
        supportModalText: "Эти реквизиты можно заменить в файле app/static/index.html.",

        allDeals: "Все скидки",
        discount90: "90%+",
        discount75: "75%+",
        under5: "Under $5",
        free: "Free",

        searchGame: "Поиск игры",
        searchPlaceholder: "Например: Witcher",
        minDiscount: "Минимальная скидка",
        maxDiscount: "Максимальная скидка",
        source: "Источник",
        sort: "Сортировка",
        sortSavings: "Сначала большая скидка",
        sortPrice: "Сначала дешевле",
        sortTitle: "По названию",
        sortStore: "По магазину",
        hideOwned: "Скрыть уже купленные",
        findDeals: "Найти скидки",

        steamLibrary: "Подключить Steam",
        steamText: "Введи SteamID64. Для синхронизации нужен STEAM_API_KEY в переменных окружения. Без ключа можно пользоваться ручным добавлением игр.",
        manualLibrary: "Добавить купленную игру",
        manualText: "Для Epic и других платформ пока можно добавлять игры вручную.",
        manualTitlePlaceholder: "Название игры",
        manualGameIdPlaceholder: "App ID optional",

        syncSteam: "Sync Steam Library",
        add: "Добавить",

        deals: "Скидки",
        myLibrary: "Моя библиотека",
        favorites: "Избранное",

        alreadyOwned: "Уже куплено",
        store: "Магазин",
        price: "Цена",
        discount: "Скидка",
        open: "Открыть",
        addFavorite: "В избранное",
        addFavoriteAnyway: "В избранное всё равно",
        delete: "Удалить",

        platform: "Платформа",
        gameId: "ID",
        playtime: "Время игры",
        targetPrice: "Целевая цена",
        notSet: "не указана",

        cardKaspi: "Kaspi / карта",
        receiver: "Получатель",
        telegram: "Telegram",
        contactMe: "Связаться со мной",
        comment: "Комментарий",

        noDeals: "Ничего не найдено. Попробуй уменьшить минимальную скидку, отключить «Скрыть уже купленные» или выбрать другой источник.",
        noFavorites: "Избранных игр пока нет.",
        noOwnedGames: "Купленных игр пока нет.",
        enterTitle: "Введи название игры.",
        enterSteamId: "Введи SteamID64.",
        syncLoading: "Синхронизация...",
        syncDone: "Готово. Синхронизировано игр:",
        games: "игр",

        loading: "Загрузка...",

        errorSources: "Ошибка загрузки источников",
        errorDeals: "Ошибка загрузки скидок",
        errorFavorites: "Ошибка загрузки избранного",
        errorLibrary: "Ошибка загрузки библиотеки",
        errorSaveFavorite: "Ошибка сохранения избранного",
        errorAddGame: "Ошибка добавления игры",
        frontendNotArray: "Frontend получил не список игр. Проверь /api/deals."
    },

    en: {
        badge: "Personal Game Deals Assistant",
        mainTitle: "Game Deals Assistant",
        subtitle: "Discounts, favorites, personal library, and already owned game marks.",

        supportTitle: "Support the Author",
        supportText: "If this project was useful, you can support its development.",
        supportButton: "Show support details",
        supportModalText: "You can replace these support details in app/static/index.html.",

        allDeals: "All deals",
        discount90: "90%+",
        discount75: "75%+",
        under5: "Under $5",
        free: "Free",

        searchGame: "Search game",
        searchPlaceholder: "For example: Witcher",
        minDiscount: "Minimum discount",
        maxDiscount: "Maximum discount",
        source: "Source",
        sort: "Sorting",
        sortSavings: "Highest discount first",
        sortPrice: "Lowest price first",
        sortTitle: "By title",
        sortStore: "By store",
        hideOwned: "Hide already owned",
        findDeals: "Find deals",

        steamLibrary: "Connect Steam",
        steamText: "Enter your SteamID64. Steam Library Sync requires STEAM_API_KEY in environment variables. Without a key, you can still add owned games manually.",
        manualLibrary: "Add owned game",
        manualText: "For Epic and other platforms, games can currently be added manually.",
        manualTitlePlaceholder: "Game title",
        manualGameIdPlaceholder: "App ID optional",

        syncSteam: "Sync Steam Library",
        add: "Add",

        deals: "Deals",
        myLibrary: "My Library",
        favorites: "Favorites",

        alreadyOwned: "Already owned",
        store: "Store",
        price: "Price",
        discount: "Discount",
        open: "Open",
        addFavorite: "Add to favorites",
        addFavoriteAnyway: "Add anyway",
        delete: "Delete",

        platform: "Platform",
        gameId: "ID",
        playtime: "Playtime",
        targetPrice: "Target price",
        notSet: "not set",

        cardKaspi: "Kaspi / card",
        receiver: "Receiver",
        telegram: "Telegram",
        contactMe: "Contact me",
        comment: "Comment",

        noDeals: "Nothing found. Try lowering the minimum discount, disabling “Hide already owned”, or choosing another source.",
        noFavorites: "No favorite games yet.",
        noOwnedGames: "No owned games yet.",
        enterTitle: "Enter a game title.",
        enterSteamId: "Enter SteamID64.",
        syncLoading: "Syncing...",
        syncDone: "Done. Synced games:",
        games: "games",

        loading: "Loading...",

        errorSources: "Source loading error",
        errorDeals: "Deals loading error",
        errorFavorites: "Favorites loading error",
        errorLibrary: "Library loading error",
        errorSaveFavorite: "Favorite saving error",
        errorAddGame: "Game adding error",
        frontendNotArray: "Frontend received something that is not a game list. Check /api/deals."
    }
};

function t(key) {
    return translations[currentLanguage][key] || key;
}

function applyLanguage() {
    document.querySelectorAll("[data-i18n]").forEach(element => {
        const key = element.dataset.i18n;
        element.textContent = t(key);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(element => {
        const key = element.dataset.i18nPlaceholder;
        element.placeholder = t(key);
    });

    const langToggleBtn = document.getElementById("langToggleBtn");

    if (langToggleBtn) {
        langToggleBtn.textContent = currentLanguage === "ru" ? "EN" : "RU";
    }

    document.documentElement.lang = currentLanguage;
}

const dealsGrid = document.getElementById("dealsGrid");
const favoritesGrid = document.getElementById("favoritesGrid");
const ownedGrid = document.getElementById("ownedGrid");
const storeSelect = document.getElementById("storeSelect");
const dealsCount = document.getElementById("dealsCount");
const ownedCount = document.getElementById("ownedCount");
const errorBox = document.getElementById("errorBox");
const steamSyncStatus = document.getElementById("steamSyncStatus");

const supportBtn = document.getElementById("supportBtn");
const supportModal = document.getElementById("supportModal");
const closeSupportBtn = document.getElementById("closeSupportBtn");

let lastDeals = [];

async function api(path, options = {}) {
    const response = await fetch(path, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || "Request failed");
    }

    return response.json();
}

function showError(message) {
    if (errorBox) {
        errorBox.textContent = message || "";
    }
}

function money(value) {
    const number = Number(value);
    return Number.isNaN(number) ? "$0.00" : `$${number.toFixed(2)}`;
}

function setupSupportModal() {
    if (!supportBtn || !supportModal || !closeSupportBtn) {
        return;
    }

    supportBtn.addEventListener("click", () => {
        supportModal.classList.remove("hidden");
    });

    closeSupportBtn.addEventListener("click", () => {
        supportModal.classList.add("hidden");
    });

    supportModal.addEventListener("click", event => {
        if (event.target === supportModal) {
            supportModal.classList.add("hidden");
        }
    });
}

async function loadStores() {
    try {
        const data = await api("/api/stores");
        storeSelect.innerHTML = "";

        data.all.forEach(store => {
            const option = document.createElement("option");
            option.value = store.store_id;
            option.textContent = store.store_name;
            storeSelect.appendChild(option);
        });
    } catch (error) {
        showError(`${t("errorSources")}: ${error.message}`);
    }
}

function sortDeals(deals) {
    const sortValue = document.getElementById("sortSelect").value;
    const sorted = [...deals];

    if (sortValue === "savings") {
        sorted.sort((a, b) => Number(b.savings) - Number(a.savings));
    }

    if (sortValue === "price") {
        sorted.sort((a, b) => Number(a.sale_price) - Number(b.sale_price));
    }

    if (sortValue === "title") {
        sorted.sort((a, b) => String(a.title || "").localeCompare(String(b.title || "")));
    }

    if (sortValue === "store") {
        sorted.sort((a, b) => String(a.store_name || "").localeCompare(String(b.store_name || "")));
    }

    return sorted;
}

function renderDeals(deals) {
    dealsGrid.innerHTML = "";

    if (!Array.isArray(deals)) {
        showError(t("frontendNotArray"));
        dealsCount.textContent = `0 ${t("games")}`;
        return;
    }

    const sortedDeals = sortDeals(deals);
    dealsCount.textContent = `${sortedDeals.length} ${t("games")}`;

    if (sortedDeals.length === 0) {
        dealsGrid.innerHTML = `
            <div class="empty-state">
                ${t("noDeals")}
            </div>
        `;
        return;
    }

    sortedDeals.forEach(deal => {
        const card = document.createElement("article");
        card.className = "card";

        const title = deal.title || "Unknown game";
        const storeName = deal.store_name || "Unknown store";
        const thumb = deal.thumb || "";
        const normalPrice = money(deal.normal_price);
        const salePrice = money(deal.sale_price);
        const savings = Number(deal.savings || 0).toFixed(2);
        const dealUrl = deal.deal_url || "#";
        const owned = Boolean(deal.owned);

        card.innerHTML = `
            <img src="${thumb}" alt="">
            <div class="card-body">
                ${owned ? `<span class="owned-badge">${t("alreadyOwned")}</span>` : ""}
                <h3>${title}</h3>

                <div class="meta">
                    <div>${t("store")}: ${storeName}</div>
                    <div>${t("price")}: <s>${normalPrice}</s> → <span class="price">${salePrice}</span></div>
                    <div class="discount">${t("discount")}: ${savings}%</div>
                </div>

                <input class="target-input" type="number" min="0" step="0.01" placeholder="Target price for alert">

                <div class="card-actions">
                    <a href="${dealUrl}" target="_blank">${t("open")}</a>
                    <button>${owned ? t("addFavoriteAnyway") : t("addFavorite")}</button>
                </div>
            </div>
        `;

        const targetInput = card.querySelector(".target-input");
        const favoriteBtn = card.querySelector("button");

        favoriteBtn.addEventListener("click", async () => {
            try {
                await api("/api/favorites", {
                    method: "POST",
                    body: JSON.stringify({
                        title,
                        store_name: storeName,
                        deal_url: dealUrl,
                        sale_price: Number(deal.sale_price || 0),
                        normal_price: Number(deal.normal_price || 0),
                        savings: Number(deal.savings || 0),
                        target_price: targetInput.value ? Number(targetInput.value) : null
                    })
                });

                await loadFavorites();
            } catch (error) {
                showError(`${t("errorSaveFavorite")}: ${error.message}`);
            }
        });

        dealsGrid.appendChild(card);
    });
}

async function loadDeals(extra = {}) {
    showError("");
    dealsGrid.innerHTML = `<p>${t("loading")}</p>`;

    const minDiscount = extra.minDiscount ?? document.getElementById("minDiscount").value;
    const maxDiscount = extra.maxDiscount ?? document.getElementById("maxDiscount").value;
    const storeId = storeSelect.value;
    const title = document.getElementById("titleSearch").value.trim();
    const hideOwned = document.getElementById("hideOwned").checked;

    const params = new URLSearchParams();
    params.append("min_discount", minDiscount);
    params.append("max_discount", maxDiscount);
    params.append("hide_owned", hideOwned ? "true" : "false");

    if (storeId === "steam_direct") {
        params.append("source", "steam");
    } else if (storeId && storeId !== "cheapshark_all") {
        params.append("store_id", storeId);
    }

    if (title) {
        params.append("title", title);
    }

    if (extra.maxPrice !== undefined) {
        params.append("max_price", extra.maxPrice);
    }

    if (extra.freeOnly) {
        params.append("free_only", "true");
    }

    try {
        lastDeals = await api(`/api/deals?${params.toString()}`);
        renderDeals(lastDeals);
    } catch (error) {
        dealsGrid.innerHTML = "";
        dealsCount.textContent = `0 ${t("games")}`;
        showError(`${t("errorDeals")}: ${error.message}`);
        console.error(error);
    }
}

async function loadFavorites() {
    try {
        const favorites = await api("/api/favorites");
        favoritesGrid.innerHTML = "";

        if (!favorites.length) {
            favoritesGrid.innerHTML = `<p class="empty-state">${t("noFavorites")}</p>`;
            return;
        }

        favorites.forEach(fav => {
            const card = document.createElement("article");
            card.className = "card";

            card.innerHTML = `
                <div class="card-body">
                    <h3>${fav.title}</h3>

                    <div class="meta">
                        <div>${t("store")}: ${fav.store_name}</div>
                        <div>${t("price")}: <s>${money(fav.normal_price)}</s> → <span class="price">${money(fav.sale_price)}</span></div>
                        <div class="discount">${t("discount")}: ${Number(fav.savings || 0).toFixed(2)}%</div>
                        <div>${t("targetPrice")}: ${fav.target_price ? money(fav.target_price) : t("notSet")}</div>
                    </div>

                    <div class="card-actions">
                        <a href="${fav.deal_url}" target="_blank">${t("open")}</a>
                        <button>${t("delete")}</button>
                    </div>
                </div>
            `;

            card.querySelector("button").addEventListener("click", async () => {
                await api(`/api/favorites/${fav.id}`, { method: "DELETE" });
                await loadFavorites();
            });

            favoritesGrid.appendChild(card);
        });
    } catch (error) {
        showError(`${t("errorFavorites")}: ${error.message}`);
    }
}

async function loadOwnedGames() {
    try {
        const games = await api("/api/owned-games");
        ownedGrid.innerHTML = "";
        ownedCount.textContent = `${games.length} ${t("games")}`;

        if (!games.length) {
            ownedGrid.innerHTML = `<p class="empty-state">${t("noOwnedGames")}</p>`;
            return;
        }

        games.forEach(game => {
            const card = document.createElement("article");
            card.className = "card";

            card.innerHTML = `
                <div class="card-body">
                    <span class="owned-badge">${t("alreadyOwned")}</span>
                    <h3>${game.title || game.platform_game_id}</h3>

                    <div class="meta">
                        <div>${t("platform")}: ${game.platform}</div>
                        <div>${t("gameId")}: ${game.platform_game_id}</div>
                        <div>${t("playtime")}: ${game.playtime_minutes || 0} min</div>
                    </div>

                    <div class="card-actions">
                        <button>${t("delete")}</button>
                    </div>
                </div>
            `;

            card.querySelector("button").addEventListener("click", async () => {
                await api(`/api/owned-games/${game.id}`, { method: "DELETE" });
                await loadOwnedGames();
                await loadDeals();
            });

            ownedGrid.appendChild(card);
        });
    } catch (error) {
        showError(`${t("errorLibrary")}: ${error.message}`);
    }
}

async function addManualOwnedGame() {
    const platform = document.getElementById("manualPlatform").value;
    const title = document.getElementById("manualTitle").value.trim();
    const platformGameId = document.getElementById("manualGameId").value.trim();

    if (!title) {
        showError(t("enterTitle"));
        return;
    }

    try {
        await api("/api/owned-games/manual", {
            method: "POST",
            body: JSON.stringify({
                platform,
                title,
                platform_game_id: platformGameId || null
            })
        });

        document.getElementById("manualTitle").value = "";
        document.getElementById("manualGameId").value = "";

        await loadOwnedGames();
        await loadDeals();
    } catch (error) {
        showError(`${t("errorAddGame")}: ${error.message}`);
    }
}

async function syncSteamLibrary() {
    const steamId = document.getElementById("steamIdInput").value.trim();

    if (!steamId) {
        showError(t("enterSteamId"));
        return;
    }

    steamSyncStatus.textContent = t("syncLoading");
    showError("");

    try {
        const result = await api("/api/steam/sync", {
            method: "POST",
            body: JSON.stringify({ steam_id: steamId })
        });

        steamSyncStatus.textContent = `${t("syncDone")} ${result.games_count}`;
        await loadOwnedGames();
        await loadDeals();
    } catch (error) {
        steamSyncStatus.textContent = "";
        showError(`Steam sync error: ${error.message}`);
    }
}

function applyPreset(preset) {
    const minDiscountInput = document.getElementById("minDiscount");
    const maxDiscountInput = document.getElementById("maxDiscount");

    if (preset === "all") {
        minDiscountInput.value = 10;
        maxDiscountInput.value = 100;
        loadDeals();
    }

    if (preset === "90") {
        minDiscountInput.value = 90;
        maxDiscountInput.value = 100;
        loadDeals();
    }

    if (preset === "75") {
        minDiscountInput.value = 75;
        maxDiscountInput.value = 100;
        loadDeals();
    }

    if (preset === "under5") {
        minDiscountInput.value = 10;
        maxDiscountInput.value = 100;
        loadDeals({ maxPrice: 5 });
    }

    if (preset === "free") {
        minDiscountInput.value = 0;
        maxDiscountInput.value = 100;
        loadDeals({ freeOnly: true });
    }
}

const loadDealsBtn = document.getElementById("loadDealsBtn");
const sortSelect = document.getElementById("sortSelect");
const hideOwnedCheckbox = document.getElementById("hideOwned");
const manualAddBtn = document.getElementById("manualAddBtn");
const syncSteamBtn = document.getElementById("syncSteamBtn");
const langToggleBtn = document.getElementById("langToggleBtn");
const titleSearch = document.getElementById("titleSearch");

if (loadDealsBtn) {
    loadDealsBtn.addEventListener("click", () => loadDeals());
}

if (sortSelect) {
    sortSelect.addEventListener("change", () => renderDeals(lastDeals));
}

if (hideOwnedCheckbox) {
    hideOwnedCheckbox.addEventListener("change", () => loadDeals());
}

if (manualAddBtn) {
    manualAddBtn.addEventListener("click", addManualOwnedGame);
}

if (syncSteamBtn) {
    syncSteamBtn.addEventListener("click", syncSteamLibrary);
}

if (langToggleBtn) {
    langToggleBtn.addEventListener("click", async () => {
        currentLanguage = currentLanguage === "ru" ? "en" : "ru";
        localStorage.setItem("language", currentLanguage);

        applyLanguage();

        if (Array.isArray(lastDeals)) {
            renderDeals(lastDeals);
        }

        try {
            await loadFavorites();
            await loadOwnedGames();
        } catch (error) {
            console.error("Language switch refresh error:", error);
        }
    });
}

document.querySelectorAll("[data-preset]").forEach(button => {
    button.addEventListener("click", () => applyPreset(button.dataset.preset));
});

if (titleSearch) {
    titleSearch.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            loadDeals();
        }
    });
}

(async function init() {
    setupSupportModal();
    applyLanguage();

    await loadStores();
    await loadDeals();
    await loadFavorites();
    await loadOwnedGames();
})();

console.log("script.js loaded");
console.log("Language button:", document.getElementById("langToggleBtn"));
console.log("i18n elements:", document.querySelectorAll("[data-i18n]").length);