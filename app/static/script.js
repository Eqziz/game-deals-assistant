/**
 * Game Deals Assistant - Frontend Controller
 */

let currentLanguage = localStorage.getItem("language") || "ru";

const translations = {
    ru: {
        badge: "Pro Tracker",
        subtitle: "Скидки, избранное, библиотека и отметка уже купленных игр.",
        supportButton: "Поддержать",

        dealsTab: "Скидки",
        favoritesTab: "Избранное",
        libraryTab: "Моя библиотека",
        syncTab: "Синхронизация",

        presetsLabel: "Быстрые фильтры:",
        allDeals: "🔥 Все скидки",
        discount90: "💥 90%+",
        discount75: "⚡ 75%+",
        under5: "💵 До $5",
        free: "🎁 Бесплатно",

        searchGame: "Поиск игры",
        searchPlaceholder: "Например: Witcher, Cyberpunk, Doom...",
        source: "Магазин / Источник",
        allStores: "Все PC магазины",
        minDiscount: "Мин. скидка (%)",
        maxDiscount: "Макс. скидка (%)",
        sort: "Сортировка",
        sortSavings: "Сначала большая скидка",
        sortPriceAsc: "Сначала дешевле",
        sortPriceDesc: "Сначала дороже",
        sortRating: "По рейтингу сделки",
        sortTitle: "По названию (A-Z)",
        sortStore: "По магазину",
        hideOwned: "Скрыть купленные",
        findDeals: "Найти скидки",
        resetFilters: "Сброс",

        dealsHeading: "Каталог скидок",
        loadMore: "Показать ещё скидки",
        loading: "Загрузка...",

        favoritesHeading: "Моё избранное",
        favoritesDesc: "Сохранённые скидки и отслеживание желаемой цены.",

        libraryHeading: "Моя библиотека игр",
        addOrSyncBtn: "➕ Добавить игру / Синхронизация",
        platformAll: "Все платформы",
        platformOther: "Другие",
        searchLibraryPlaceholder: "Поиск в библиотеке...",

        autoSync: "Автосинхронизация",
        steamLibrary: "Синхронизация со Steam",
        steamText: "Введи свой SteamID64 (17-значный цифровой ID профиля). Игры с временем игры добавятся в библиотеку и будут скрываться из скидок при включённом фильтре.",
        syncSteam: "Синхронизировать",
        steamIdHelper: "Как узнать SteamID64? Открой свой профиль Steam или используй сервис steamid.io. Профиль должен быть открытым.",

        anyPlatform: "Любые сервисы",
        manualLibrary: "Ручное добавление игры",
        manualText: "Добавляй купленные игры из Epic Games Store, GOG, EA App, VK Play или других источников.",
        platformLabel: "Платформа",
        gameTitleLabel: "Название игры *",
        manualTitlePlaceholder: "Например: Red Dead Redemption 2",
        appIdOptional: "App ID (опционально)",
        manualGameIdPlaceholder: "Например: 1174180",
        playtimeOptional: "Сыграно (часов)",
        addGameBtn: "➕ Добавить в библиотеку",

        targetPriceModalTitle: "Оповещение о цене",
        currentPrice: "Текущая цена",
        normalPrice: "Обычная цена",
        targetPriceInputLabel: "Желаемая цена ($):",
        targetPriceHint: "Игра будет сохранена в избранное с отслеживанием этой суммы.",
        cancelBtn: "Отмена",
        saveAlertBtn: "Сохранить оповещение",

        supportTitle: "Поддержать автора",
        supportText: "Если проект оказался полезным, вы можете поддержать развитие.",
        cardKaspi: "Банковская карта (Kaspi / Visa)",
        receiver: "Получатель",
        telegram: "Telegram",
        contactMe: "Email для связи",
        copyBtn: "Копировать",
        copiedBtn: "Скопировано!",

        alreadyOwned: "В библиотеке",
        freeGame: "БЕСПЛАТНО",
        openDeal: "В магазин",
        hours: "ч",
        targetReached: "🎯 Цель достигнута!",
        targetSet: "Цель:",

        noDeals: "Ничего не найдено. Попробуйте изменить фильтры или сбросить поиск.",
        noFavorites: "В избранном пока пусто. Нажмите ⭐ на карточке любой игры в каталоге.",
        noOwnedGames: "Библиотека пуста. Добавьте игру вручную или синхронизируйте со Steam.",
        noSearchResults: "По запросу ничего не найдено в библиотеке.",

        toastFavAdded: "Добавлено в избранное ⭐",
        toastFavRemoved: "Удалено из избранного",
        toastGameAdded: "Игра добавлена в библиотеку 📚",
        toastGameDeleted: "Игра удалена из библиотеки",
        toastSteamSynced: "Steam синхронизирован! Добавлено игр:",
        toastCopied: "Скопировано в буфер обмена 📋",
        toastError: "Произошла ошибка:",

        enterTitle: "Пожалуйста, введите название игры.",
        enterSteamId: "Пожалуйста, введите корректный SteamID64.",
        games: "игр",
    },

    en: {
        badge: "Pro Tracker",
        subtitle: "Discounts, favorites, game library, and owned game tracking.",
        supportButton: "Support",

        dealsTab: "Deals",
        favoritesTab: "Favorites",
        libraryTab: "My Library",
        syncTab: "Sync & Accounts",

        presetsLabel: "Quick filters:",
        allDeals: "🔥 All deals",
        discount90: "💥 90%+",
        discount75: "⚡ 75%+",
        under5: "💵 Under $5",
        free: "🎁 Free Games",

        searchGame: "Game search",
        searchPlaceholder: "For example: Witcher, Cyberpunk, Doom...",
        source: "Store / Source",
        allStores: "All PC Stores",
        minDiscount: "Min discount (%)",
        maxDiscount: "Max discount (%)",
        sort: "Sorting",
        sortSavings: "Highest discount first",
        sortPriceAsc: "Lowest price first",
        sortPriceDesc: "Highest price first",
        sortRating: "By deal rating",
        sortTitle: "By title (A-Z)",
        sortStore: "By store",
        hideOwned: "Hide owned games",
        findDeals: "Find deals",
        resetFilters: "Reset",

        dealsHeading: "Deals Catalog",
        loadMore: "Load more deals",
        loading: "Loading...",

        favoritesHeading: "My Favorites",
        favoritesDesc: "Saved deals and target price monitoring.",

        libraryHeading: "My Game Library",
        addOrSyncBtn: "➕ Add Game / Sync",
        platformAll: "All platforms",
        platformOther: "Other",
        searchLibraryPlaceholder: "Search in library...",

        autoSync: "Auto-sync",
        steamLibrary: "Steam Library Sync",
        steamText: "Enter your SteamID64 (17-digit Steam profile ID). Games with playtime will be imported into your library and hidden from deals when enabled.",
        syncSteam: "Sync Library",
        steamIdHelper: "Where to find SteamID64? Check your Steam profile URL or use steamid.io. Profile must be public.",

        anyPlatform: "Any service",
        manualLibrary: "Manual Game Entry",
        manualText: "Add owned games from Epic Games Store, GOG, EA App, or other platforms.",
        platformLabel: "Platform",
        gameTitleLabel: "Game title *",
        manualTitlePlaceholder: "For example: Red Dead Redemption 2",
        appIdOptional: "App ID (optional)",
        manualGameIdPlaceholder: "For example: 1174180",
        playtimeOptional: "Playtime (hours)",
        addGameBtn: "➕ Add to Library",

        targetPriceModalTitle: "Price Alert",
        currentPrice: "Current price",
        normalPrice: "Normal price",
        targetPriceInputLabel: "Target price ($):",
        targetPriceHint: "The game will be added to favorites with this target price alert.",
        cancelBtn: "Cancel",
        saveAlertBtn: "Save alert",

        supportTitle: "Support the Author",
        supportText: "If you found this tool useful, feel free to support its development.",
        cardKaspi: "Bank Card (Kaspi / Visa)",
        receiver: "Receiver",
        telegram: "Telegram",
        contactMe: "Contact email",
        copyBtn: "Copy",
        copiedBtn: "Copied!",

        alreadyOwned: "In Library",
        freeGame: "FREE",
        openDeal: "Open Store",
        hours: "hrs",
        targetReached: "🎯 Target reached!",
        targetSet: "Target:",

        noDeals: "No deals found. Try adjusting filters or resetting search.",
        noFavorites: "No favorites yet. Click ⭐ on any deal card in the catalog.",
        noOwnedGames: "Your library is empty. Add a game manually or sync with Steam.",
        noSearchResults: "No matching games in your library.",

        toastFavAdded: "Added to favorites ⭐",
        toastFavRemoved: "Removed from favorites",
        toastGameAdded: "Game added to library 📚",
        toastGameDeleted: "Game removed from library",
        toastSteamSynced: "Steam synced! Added games:",
        toastCopied: "Copied to clipboard 📋",
        toastError: "An error occurred:",

        enterTitle: "Please enter a game title.",
        enterSteamId: "Please enter a valid SteamID64.",
        games: "games",
    }
};

function t(key) {
    const langDict = translations[currentLanguage] || translations.ru;
    return langDict[key] || (translations.en && translations.en[key]) || key;
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

    const langLabel = document.getElementById("langLabel");
    if (langLabel) {
        langLabel.textContent = currentLanguage === "ru" ? "EN" : "RU";
    }

    document.documentElement.lang = currentLanguage;
}

// Global state
let lastDeals = [];
let nextDealsPage = null;
let currentDealsExtra = {};
let currentPreset = "all";
let cachedFavorites = [];
let cachedOwnedGames = [];
let targetModalDeal = null;
let searchDebounceTimer = null;

// DOM Elements
const dealsGrid = document.getElementById("dealsGrid");
const loadMoreBtn = document.getElementById("loadMoreBtn");
const favoritesGrid = document.getElementById("favoritesGrid");
const ownedGrid = document.getElementById("ownedGrid");
const storeSelect = document.getElementById("storeSelect");
const sortSelect = document.getElementById("sortSelect");
const titleSearch = document.getElementById("titleSearch");
const clearSearchBtn = document.getElementById("clearSearchBtn");
const minDiscountInput = document.getElementById("minDiscount");
const maxDiscountInput = document.getElementById("maxDiscount");
const hideOwnedCheckbox = document.getElementById("hideOwned");
const loadDealsBtn = document.getElementById("loadDealsBtn");
const resetFiltersBtn = document.getElementById("resetFiltersBtn");
const errorBox = document.getElementById("errorBox");

const dealsCount = document.getElementById("dealsCount");
const dealsCountBadge = document.getElementById("dealsCountBadge");
const favCountBadge = document.getElementById("favCountBadge");
const favoritesCount = document.getElementById("favoritesCount");
const libraryCount = document.getElementById("libraryCount");
const libraryCountBadge = document.getElementById("libraryCountBadge");

const toastContainer = document.getElementById("toastContainer");
const targetPriceModal = document.getElementById("targetPriceModal");
const supportModal = document.getElementById("supportModal");

// API helper
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
        throw new Error(error.detail || `Request failed (${response.status})`);
    }

    return response.json();
}

function showToast(message, type = "info") {
    if (!toastContainer) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("fade-out");
        setTimeout(() => toast.remove(), 220);
    }, 2800);
}

function showError(message) {
    if (!errorBox) return;
    if (!message) {
        errorBox.textContent = "";
        errorBox.classList.add("hidden");
    } else {
        errorBox.textContent = message;
        errorBox.classList.remove("hidden");
    }
}

function money(value) {
    const num = Number(value);
    if (Number.isNaN(num) || num <= 0) {
        return "$0.00";
    }
    return `$${num.toFixed(2)}`;
}

// Fallback image generator
function getPlaceholderSvg(title = "") {
    const safeTitle = (title || "Game").slice(0, 24);
    return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="300" height="170" viewBox="0 0 300 170"><rect width="100%" height="100%" fill="%23141724"/><text x="50%" y="45%" font-size="34" text-anchor="middle" fill="%234338ca">🎮</text><text x="50%" y="70%" font-size="13" font-family="sans-serif" font-weight="bold" text-anchor="middle" fill="%2394a3b8">${encodeURIComponent(safeTitle)}</text></svg>`;
}

// TABS HANDLING
function setupTabs() {
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.dataset.tab;

            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const pane = document.getElementById(`tab-${targetTab}`);
            if (pane) {
                pane.classList.add("active");
            }
        });
    });

    const jumpToSyncBtn = document.getElementById("jumpToSyncBtn");
    if (jumpToSyncBtn) {
        jumpToSyncBtn.addEventListener("click", () => {
            const syncTabBtn = document.querySelector('.tab-btn[data-tab="sync"]');
            if (syncTabBtn) syncTabBtn.click();
        });
    }
}

// STORE LIST
async function loadStores() {
    try {
        const data = await api("/api/stores");
        if (!storeSelect) return;

        storeSelect.innerHTML = "";

        const allStoresOpt = document.createElement("option");
        allStoresOpt.value = "cheapshark_all";
        allStoresOpt.textContent = t("allStores");
        storeSelect.appendChild(allStoresOpt);

        data.all.forEach(store => {
            if (store.store_id === "cheapshark_all") return;
            const option = document.createElement("option");
            option.value = store.store_id;
            option.textContent = store.store_name;
            storeSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Store loading error:", error);
    }
}

// DEALS SORTING
function sortDealsList(deals) {
    const sortVal = sortSelect ? sortSelect.value : "savings";
    const sorted = [...deals];

    if (sortVal === "savings") {
        sorted.sort((a, b) => Number(b.savings || 0) - Number(a.savings || 0));
    } else if (sortVal === "price_asc") {
        sorted.sort((a, b) => Number(a.sale_price || 0) - Number(b.sale_price || 0));
    } else if (sortVal === "price_desc") {
        sorted.sort((a, b) => Number(b.sale_price || 0) - Number(a.sale_price || 0));
    } else if (sortVal === "rating") {
        sorted.sort((a, b) => Number(b.deal_rating || 0) - Number(a.deal_rating || 0));
    } else if (sortVal === "title") {
        sorted.sort((a, b) => String(a.title || "").localeCompare(String(b.title || "")));
    } else if (sortVal === "store") {
        sorted.sort((a, b) => String(a.store_name || "").localeCompare(String(b.store_name || "")));
    }

    return sorted;
}

// SKELETON CARDS
function renderSkeletons(count = 12) {
    if (!dealsGrid) return;
    dealsGrid.innerHTML = "";
    for (let i = 0; i < count; i++) {
        const skel = document.createElement("div");
        skel.className = "skeleton-card";
        skel.innerHTML = `
            <div class="skeleton-media"></div>
            <div class="skeleton-body">
                <div class="skeleton-line w-70"></div>
                <div class="skeleton-line w-90"></div>
                <div class="skeleton-line w-40"></div>
            </div>
        `;
        dealsGrid.appendChild(skel);
    }
}

// RENDER DEALS
function renderDeals(deals) {
    if (!dealsGrid) return;
    dealsGrid.innerHTML = "";

    if (!Array.isArray(deals)) {
        showError("Invalid deals response format");
        return;
    }

    const sorted = sortDealsList(deals);
    const countText = `${sorted.length} ${t("games")}`;
    if (dealsCount) dealsCount.textContent = countText;
    if (dealsCountBadge) dealsCountBadge.textContent = sorted.length;

    if (sorted.length === 0) {
        dealsGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🎮</div>
                <h3>${t("noDeals")}</h3>
                <button class="btn btn-secondary" onclick="document.getElementById('resetFiltersBtn').click()">
                    ${t("resetFilters")}
                </button>
            </div>
        `;
        updateLoadMoreButton();
        return;
    }

    const favUrls = new Set(cachedFavorites.map(f => f.deal_url));

    sorted.forEach(deal => {
        const card = document.createElement("article");
        card.className = "card";

        const title = deal.title || "Unknown game";
        const storeName = deal.store_name || "PC Store";
        const storeIcon = deal.store_icon;
        const thumb = deal.thumb || "";
        const normalPriceVal = Number(deal.normal_price || 0);
        const salePriceVal = Number(deal.sale_price || 0);
        const savings = Math.round(Number(deal.savings || 0));
        const dealUrl = deal.deal_url || "#";
        const owned = Boolean(deal.owned);
        const isFav = deal.is_favorite || favUrls.has(dealUrl);
        const isFree = salePriceVal === 0;

        const steamRating = deal.steam_rating_percent;
        const metacritic = deal.metacritic_score;

        const fallbackImg = getPlaceholderSvg(title);

        card.innerHTML = `
            <div class="card-media">
                <img
                    src="${thumb || fallbackImg}"
                    alt="${title}"
                    loading="lazy"
                    onerror="this.onerror=null;this.src='${fallbackImg}'"
                >
                <div class="floating-discount">-${savings}%</div>
                <div class="floating-store">
                    ${storeIcon ? `<img src="${storeIcon}" alt="">` : ""}
                    <span>${storeName}</span>
                </div>
            </div>

            <div class="card-content">
                <div class="card-badges-row">
                    ${owned ? `<span class="owned-badge">✓ ${t("alreadyOwned")}</span>` : ""}
                    ${steamRating ? `<span class="rating-badge">★ ${steamRating}%</span>` : ""}
                    ${metacritic ? `<span class="metacritic-badge" title="Metacritic">${metacritic}</span>` : ""}
                </div>

                <h3 class="card-title" title="${title}">${title}</h3>

                <div class="card-pricing">
                    <span class="price-strike">${money(normalPriceVal)}</span>
                    ${isFree
                        ? `<span class="price-free">${t("freeGame")}</span>`
                        : `<span class="price-current">${money(salePriceVal)}</span>`
                    }
                </div>

                <div class="card-actions-bar">
                    <a href="${dealUrl}" target="_blank" rel="noopener noreferrer" class="open-deal-btn">
                        <span>${t("openDeal")}</span> ↗
                    </a>
                    <button class="fav-toggle-btn ${isFav ? "active" : ""}" title="${isFav ? t("toastFavRemoved") : t("toastFavAdded")}">
                        ${isFav ? "★" : "☆"}
                    </button>
                    <button class="alert-toggle-btn" title="${t("targetPriceModalTitle")}">
                        🔔
                    </button>
                </div>
            </div>
        `;

        // Favorite Toggle
        const favBtn = card.querySelector(".fav-toggle-btn");
        favBtn.addEventListener("click", async () => {
            const currentlyFav = favBtn.classList.contains("active");
            if (currentlyFav) {
                try {
                    await api("/api/favorites/delete-by-url", {
                        method: "POST",
                        body: JSON.stringify({ deal_url: dealUrl })
                    });
                    favBtn.classList.remove("active");
                    favBtn.textContent = "☆";
                    deal.is_favorite = false;
                    showToast(t("toastFavRemoved"));
                    await loadFavorites();
                } catch (err) {
                    showToast(`${t("toastError")} ${err.message}`, "error");
                }
            } else {
                try {
                    await api("/api/favorites", {
                        method: "POST",
                        body: JSON.stringify({
                            title,
                            store_name: storeName,
                            deal_url: dealUrl,
                            sale_price: salePriceVal,
                            normal_price: normalPriceVal,
                            savings: Number(deal.savings || 0),
                            target_price: null
                        })
                    });
                    favBtn.classList.add("active");
                    favBtn.textContent = "★";
                    deal.is_favorite = true;
                    showToast(t("toastFavAdded"));
                    await loadFavorites();
                } catch (err) {
                    showToast(`${t("toastError")} ${err.message}`, "error");
                }
            }
        });

        // Price Alert Modal button
        const alertBtn = card.querySelector(".alert-toggle-btn");
        alertBtn.addEventListener("click", () => {
            openTargetPriceModal(deal);
        });

        dealsGrid.appendChild(card);
    });

    updateLoadMoreButton();
}

// TARGET PRICE MODAL
function openTargetPriceModal(deal) {
    if (!targetPriceModal) return;
    targetModalDeal = deal;

    const gameTitleEl = document.getElementById("targetModalGameTitle");
    const currentPriceEl = document.getElementById("targetModalCurrentPrice");
    const normalPriceEl = document.getElementById("targetModalNormalPrice");
    const targetInput = document.getElementById("targetPriceInput");

    if (gameTitleEl) gameTitleEl.textContent = deal.title || "";
    if (currentPriceEl) currentPriceEl.textContent = money(deal.sale_price);
    if (normalPriceEl) normalPriceEl.textContent = money(deal.normal_price);
    if (targetInput) {
        const suggested = Math.max(0.99, Number(deal.sale_price || 0) * 0.8).toFixed(2);
        targetInput.value = suggested;
    }

    targetPriceModal.classList.remove("hidden");
}

function setupTargetPriceModal() {
    if (!targetPriceModal) return;

    document.querySelectorAll('[data-close="targetPriceModal"]').forEach(el => {
        el.addEventListener("click", () => {
            targetPriceModal.classList.add("hidden");
        });
    });

    targetPriceModal.addEventListener("click", (e) => {
        if (e.target === targetPriceModal) {
            targetPriceModal.classList.add("hidden");
        }
    });

    const saveBtn = document.getElementById("saveTargetPriceBtn");
    if (saveBtn) {
        saveBtn.addEventListener("click", async () => {
            if (!targetModalDeal) return;
            const targetInput = document.getElementById("targetPriceInput");
            const targetVal = targetInput && targetInput.value ? Number(targetInput.value) : null;

            try {
                await api("/api/favorites", {
                    method: "POST",
                    body: JSON.stringify({
                        title: targetModalDeal.title,
                        store_name: targetModalDeal.store_name,
                        deal_url: targetModalDeal.deal_url,
                        sale_price: Number(targetModalDeal.sale_price || 0),
                        normal_price: Number(targetModalDeal.normal_price || 0),
                        savings: Number(targetModalDeal.savings || 0),
                        target_price: targetVal
                    })
                });

                targetPriceModal.classList.add("hidden");
                showToast(t("toastFavAdded"));
                await loadFavorites();
                await loadDeals(currentDealsExtra, false, true);
            } catch (err) {
                showToast(`${t("toastError")} ${err.message}`, "error");
            }
        });
    }
}

// LOAD DEALS API
async function loadDeals(extra = {}, append = false, silent = false) {
    showError("");

    if (!append && !silent) {
        renderSkeletons(12);
        lastDeals = [];
        nextDealsPage = null;
        currentDealsExtra = extra;
        updateLoadMoreButton();
    }

    const pageToLoad = append ? nextDealsPage : 0;
    if (pageToLoad === null) return;

    const minDisc = extra.minDiscount ?? (minDiscountInput ? minDiscountInput.value : 10);
    const maxDisc = extra.maxDiscount ?? (maxDiscountInput ? maxDiscountInput.value : 100);
    const storeId = storeSelect ? storeSelect.value : "cheapshark_all";
    const title = titleSearch ? titleSearch.value.trim() : "";
    const hideOwned = hideOwnedCheckbox ? hideOwnedCheckbox.checked : false;

    const params = new URLSearchParams();
    params.append("min_discount", minDisc);
    params.append("max_discount", maxDisc);
    params.append("hide_owned", hideOwned ? "true" : "false");
    params.append("page", pageToLoad);
    params.append("page_size", 60);

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
        const response = await api(`/api/deals?${params.toString()}`);
        const newDeals = Array.isArray(response) ? response : (response.deals || []);
        nextDealsPage = Array.isArray(response) ? null : response.next_page;

        lastDeals = append ? [...lastDeals, ...newDeals] : newDeals;
        renderDeals(lastDeals);
    } catch (error) {
        if (!append) {
            if (dealsGrid) dealsGrid.innerHTML = "";
            if (dealsCount) dealsCount.textContent = `0 ${t("games")}`;
        }
        showError(`${t("toastError")} ${error.message}`);
        console.error("Deals error:", error);
        updateLoadMoreButton();
    }
}

function updateLoadMoreButton() {
    if (!loadMoreBtn) return;
    if (nextDealsPage === null) {
        loadMoreBtn.classList.add("hidden");
    } else {
        loadMoreBtn.classList.remove("hidden");
        loadMoreBtn.disabled = false;
        loadMoreBtn.textContent = t("loadMore");
    }
}

async function loadMoreDeals() {
    if (nextDealsPage === null || !loadMoreBtn) return;
    loadMoreBtn.disabled = true;
    loadMoreBtn.textContent = t("loading");

    await loadDeals(currentDealsExtra, true);
}

// FAVORITES
async function loadFavorites() {
    try {
        const favorites = await api("/api/favorites");
        cachedFavorites = favorites || [];

        if (favCountBadge) favCountBadge.textContent = cachedFavorites.length;
        if (favoritesCount) favoritesCount.textContent = `${cachedFavorites.length} ${t("games")}`;

        if (!favoritesGrid) return;
        favoritesGrid.innerHTML = "";

        if (!cachedFavorites.length) {
            favoritesGrid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⭐</div>
                    <h3>${t("noFavorites")}</h3>
                    <button class="btn btn-secondary" onclick="document.querySelector('.tab-btn[data-tab=\\'deals\\']').click()">
                        ${t("dealsHeading")}
                    </button>
                </div>
            `;
            return;
        }

        cachedFavorites.forEach(fav => {
            const card = document.createElement("article");
            card.className = "card";

            const normalPrice = Number(fav.normal_price || 0);
            const salePrice = Number(fav.sale_price || 0);
            const targetPrice = fav.target_price !== null && fav.target_price !== undefined ? Number(fav.target_price) : null;
            const savings = Math.round(Number(fav.savings || 0));
            const isTargetReached = targetPrice !== null && salePrice <= targetPrice;

            card.innerHTML = `
                <div class="card-content">
                    <div class="card-badges-row">
                        <span class="floating-store" style="position:static; margin-bottom: 4px;">${fav.store_name}</span>
                        ${savings > 0 ? `<span class="floating-discount" style="position:static; box-shadow:none;">-${savings}%</span>` : ""}
                    </div>

                    <h3 class="card-title">${fav.title}</h3>

                    ${targetPrice !== null ? `
                        <div class="target-badge ${isTargetReached ? "target-reached-badge" : ""}">
                            ${isTargetReached ? t("targetReached") : `${t("targetSet")} ${money(targetPrice)}`}
                        </div>
                    ` : ""}

                    <div class="card-pricing">
                        ${normalPrice > salePrice ? `<span class="price-strike">${money(normalPrice)}</span>` : ""}
                        <span class="price-current">${money(salePrice)}</span>
                    </div>

                    <div class="card-actions-bar">
                        <a href="${fav.deal_url}" target="_blank" rel="noopener noreferrer" class="open-deal-btn">
                            ${t("openDeal")} ↗
                        </a>
                        <button class="delete-btn" title="Удалить из избранного">
                            🗑️
                        </button>
                    </div>
                </div>
            `;

            card.querySelector(".delete-btn").addEventListener("click", async () => {
                try {
                    await api(`/api/favorites/${fav.id}`, { method: "DELETE" });
                    showToast(t("toastFavRemoved"));
                    await loadFavorites();
                    if (Array.isArray(lastDeals)) {
                        renderDeals(lastDeals);
                    }
                } catch (err) {
                    showToast(`${t("toastError")} ${err.message}`, "error");
                }
            });

            favoritesGrid.appendChild(card);
        });
    } catch (err) {
        console.error("Favorites error:", err);
    }
}

// OWNED GAMES / LIBRARY
async function loadOwnedGames() {
    try {
        const games = await api("/api/owned-games");
        cachedOwnedGames = games || [];

        if (libraryCountBadge) libraryCountBadge.textContent = cachedOwnedGames.length;
        if (libraryCount) libraryCount.textContent = `${cachedOwnedGames.length} ${t("games")}`;

        renderLibraryList();
    } catch (err) {
        console.error("Library load error:", err);
    }
}

function renderLibraryList(filterPlatform = "all", searchQuery = "") {
    if (!ownedGrid) return;
    ownedGrid.innerHTML = "";

    let filtered = [...cachedOwnedGames];

    if (filterPlatform && filterPlatform !== "all") {
        filtered = filtered.filter(g => (g.platform || "").toLowerCase() === filterPlatform.toLowerCase());
    }

    if (searchQuery) {
        const q = searchQuery.toLowerCase();
        filtered = filtered.filter(g => (g.title || "").toLowerCase().includes(q));
    }

    if (!filtered.length) {
        ownedGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📚</div>
                <h3>${cachedOwnedGames.length === 0 ? t("noOwnedGames") : t("noSearchResults")}</h3>
                ${cachedOwnedGames.length === 0 ? `
                    <button class="btn btn-secondary" onclick="document.querySelector('.tab-btn[data-tab=\\'sync\\']').click()">
                        ${t("addOrSyncBtn")}
                    </button>
                ` : ""}
            </div>
        `;
        return;
    }

    filtered.forEach(game => {
        const card = document.createElement("article");
        card.className = "lib-card";

        const platform = (game.platform || "other").toLowerCase();
        const platformClass = `platform-${platform}`;
        const playtimeHours = (Number(game.playtime_minutes || 0) / 60).toFixed(1);

        card.innerHTML = `
            <div class="lib-header">
                <span class="platform-pill ${platformClass}">${game.platform}</span>
                <button class="delete-btn" style="width:30px;height:30px;font-size:13px;" title="Удалить">✕</button>
            </div>
            <h4>${game.title || game.platform_game_id}</h4>
            <div class="lib-meta">
                ${game.platform_game_id ? `<div>ID: ${game.platform_game_id}</div>` : ""}
                ${Number(playtimeHours) > 0 ? `<div>⏱️ ${playtimeHours} ${t("hours")}</div>` : ""}
            </div>
        `;

        card.querySelector(".delete-btn").addEventListener("click", async () => {
            try {
                await api(`/api/owned-games/${game.id}`, { method: "DELETE" });
                showToast(t("toastGameDeleted"));
                await loadOwnedGames();
                await loadDeals(currentDealsExtra, false, true);
            } catch (err) {
                showToast(`${t("toastError")} ${err.message}`, "error");
            }
        });

        ownedGrid.appendChild(card);
    });
}

function setupLibraryFilters() {
    const pills = document.querySelectorAll(".lib-pill");
    const searchInput = document.getElementById("librarySearchInput");

    let activePlatform = "all";

    pills.forEach(pill => {
        pill.addEventListener("click", () => {
            pills.forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            activePlatform = pill.dataset.platform;
            renderLibraryList(activePlatform, searchInput ? searchInput.value.trim() : "");
        });
    });

    if (searchInput) {
        searchInput.addEventListener("input", () => {
            renderLibraryList(activePlatform, searchInput.value.trim());
        });
    }
}

// STEAM SYNC
function setupSteamSync() {
    const syncBtn = document.getElementById("syncSteamBtn");
    const steamInput = document.getElementById("steamIdInput");
    const statusText = document.getElementById("steamSyncStatus");

    if (!syncBtn || !steamInput) return;

    syncBtn.addEventListener("click", async () => {
        const steamId = steamInput.value.trim();
        if (!steamId) {
            showToast(t("enterSteamId"), "error");
            return;
        }

        syncBtn.disabled = true;
        statusText.textContent = t("loading");
        statusText.style.color = "var(--text-muted)";

        try {
            const res = await api("/api/steam/sync", {
                method: "POST",
                body: JSON.stringify({ steam_id: steamId })
            });

            statusText.textContent = `✓ ${t("toastSteamSynced")} ${res.games_count}`;
            statusText.style.color = "var(--accent-green)";
            showToast(`${t("toastSteamSynced")} ${res.games_count}`);

            await loadOwnedGames();
            await loadDeals(currentDealsExtra, false, true);
        } catch (err) {
            statusText.textContent = `✕ ${err.message}`;
            statusText.style.color = "var(--accent-red)";
            showToast(`${t("toastError")} ${err.message}`, "error");
        } finally {
            syncBtn.disabled = false;
        }
    });
}

// MANUAL ADD GAME
function setupManualAdd() {
    const form = document.getElementById("manualAddForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const platform = document.getElementById("manualPlatform").value;
        const title = document.getElementById("manualTitle").value.trim();
        const gameId = document.getElementById("manualGameId").value.trim();
        const playtimeHours = Number(document.getElementById("manualPlaytime").value || 0);

        if (!title) {
            showToast(t("enterTitle"), "error");
            return;
        }

        try {
            await api("/api/owned-games/manual", {
                method: "POST",
                body: JSON.stringify({
                    platform,
                    title,
                    platform_game_id: gameId || null,
                    playtime_minutes: Math.round(playtimeHours * 60)
                })
            });

            form.reset();
            showToast(t("toastGameAdded"));
            await loadOwnedGames();
            await loadDeals(currentDealsExtra, false, true);
        } catch (err) {
            showToast(`${t("toastError")} ${err.message}`, "error");
        }
    });
}

// PRESETS
function applyPreset(presetName) {
    currentPreset = presetName;

    document.querySelectorAll(".preset-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.preset === presetName);
    });

    if (presetName === "all") {
        if (minDiscountInput) minDiscountInput.value = 10;
        if (maxDiscountInput) maxDiscountInput.value = 100;
        loadDeals();
    } else if (presetName === "90") {
        if (minDiscountInput) minDiscountInput.value = 90;
        if (maxDiscountInput) maxDiscountInput.value = 100;
        loadDeals();
    } else if (presetName === "75") {
        if (minDiscountInput) minDiscountInput.value = 75;
        if (maxDiscountInput) maxDiscountInput.value = 100;
        loadDeals();
    } else if (presetName === "under5") {
        if (minDiscountInput) minDiscountInput.value = 10;
        if (maxDiscountInput) maxDiscountInput.value = 100;
        loadDeals({ maxPrice: 5 });
    } else if (presetName === "free") {
        if (minDiscountInput) minDiscountInput.value = 0;
        if (maxDiscountInput) maxDiscountInput.value = 100;
        loadDeals({ freeOnly: true });
    }
}

// SUPPORT MODAL & COPY TO CLIPBOARD
function setupSupportModal() {
    const supportBtn = document.getElementById("supportBtn");
    const closeBtn = document.getElementById("closeSupportBtn");

    if (supportBtn && supportModal) {
        supportBtn.addEventListener("click", () => {
            supportModal.classList.remove("hidden");
        });
    }

    if (closeBtn && supportModal) {
        closeBtn.addEventListener("click", () => {
            supportModal.classList.add("hidden");
        });
    }

    if (supportModal) {
        supportModal.addEventListener("click", (e) => {
            if (e.target === supportModal) {
                supportModal.classList.add("hidden");
            }
        });
    }

    document.querySelectorAll("[data-copy]").forEach(btn => {
        btn.addEventListener("click", async () => {
            const textToCopy = btn.dataset.copy;
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(textToCopy);
                } else {
                    const temp = document.createElement("input");
                    temp.value = textToCopy;
                    document.body.appendChild(temp);
                    temp.select();
                    document.execCommand("copy");
                    temp.remove();
                }

                btn.classList.add("copied");
                const textSpan = btn.querySelector(".copy-text");
                if (textSpan) textSpan.textContent = t("copiedBtn");
                showToast(t("toastCopied"));

                setTimeout(() => {
                    btn.classList.remove("copied");
                    if (textSpan) textSpan.textContent = t("copyBtn");
                }, 2000);
            } catch (err) {
                console.error("Copy failed:", err);
            }
        });
    });
}

// SEARCH WITH DEBOUNCE
function setupSearch() {
    if (!titleSearch) return;

    titleSearch.addEventListener("input", () => {
        if (clearSearchBtn) {
            clearSearchBtn.classList.toggle("hidden", !titleSearch.value);
        }

        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            loadDeals();
        }, 450);
    });

    titleSearch.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            clearTimeout(searchDebounceTimer);
            loadDeals();
        }
    });

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener("click", () => {
            titleSearch.value = "";
            clearSearchBtn.classList.add("hidden");
            loadDeals();
        });
    }
}

// RESET FILTERS
function setupResetFilters() {
    if (!resetFiltersBtn) return;

    resetFiltersBtn.addEventListener("click", () => {
        if (titleSearch) {
            titleSearch.value = "";
            if (clearSearchBtn) clearSearchBtn.classList.add("hidden");
        }
        if (minDiscountInput) minDiscountInput.value = 10;
        if (maxDiscountInput) maxDiscountInput.value = 100;
        if (storeSelect) storeSelect.value = "cheapshark_all";
        if (sortSelect) sortSelect.value = "savings";
        if (hideOwnedCheckbox) hideOwnedCheckbox.checked = false;

        applyPreset("all");
    });
}

// LANGUAGE SWITCHER
function setupLanguage() {
    const langBtn = document.getElementById("langToggleBtn");
    if (!langBtn) return;

    langBtn.addEventListener("click", () => {
        currentLanguage = currentLanguage === "ru" ? "en" : "ru";
        localStorage.setItem("language", currentLanguage);

        applyLanguage();
        if (Array.isArray(lastDeals)) {
            renderDeals(lastDeals);
        }
        renderLibraryList();
        loadFavorites();
    });
}

// INITIALIZATION
(async function init() {
    applyLanguage();
    setupTabs();
    setupLanguage();
    setupSupportModal();
    setupTargetPriceModal();
    setupSearch();
    setupResetFilters();
    setupLibraryFilters();
    setupSteamSync();
    setupManualAdd();

    // Event listeners
    if (loadDealsBtn) {
        loadDealsBtn.addEventListener("click", () => loadDeals());
    }

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener("click", loadMoreDeals);
    }

    if (sortSelect) {
        sortSelect.addEventListener("change", () => renderDeals(lastDeals));
    }

    if (hideOwnedCheckbox) {
        hideOwnedCheckbox.addEventListener("change", () => loadDeals());
    }

    if (storeSelect) {
        storeSelect.addEventListener("change", () => loadDeals());
    }

    document.querySelectorAll("[data-preset]").forEach(btn => {
        btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
    });

    // Initial data loading
    await loadStores();
    await loadFavorites();
    await loadOwnedGames();
    await loadDeals();
})();