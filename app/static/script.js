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
    errorBox.textContent = message || "";
}

function money(value) {
    const number = Number(value);
    return Number.isNaN(number) ? "$0.00" : `$${number.toFixed(2)}`;
}

function setupSupportModal() {
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
        showError(`Ошибка загрузки источников: ${error.message}`);
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
        showError("Frontend получил не список игр. Проверь /api/deals.");
        dealsCount.textContent = "0 найдено";
        return;
    }

    const sortedDeals = sortDeals(deals);
    dealsCount.textContent = `${sortedDeals.length} найдено`;

    if (sortedDeals.length === 0) {
        dealsGrid.innerHTML = `
            <div class="empty-state">
                Ничего не найдено. Попробуй уменьшить минимальную скидку,
                отключить "Скрыть уже купленные" или выбрать другой источник.
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
                ${owned ? `<span class="owned-badge">Уже куплено</span>` : ""}
                <h3>${title}</h3>

                <div class="meta">
                    <div>Магазин: ${storeName}</div>
                    <div>Цена: <s>${normalPrice}</s> → <span class="price">${salePrice}</span></div>
                    <div class="discount">Скидка: ${savings}%</div>
                </div>

                <input class="target-input" type="number" min="0" step="0.01" placeholder="Target price for alert">

                <div class="card-actions">
                    <a href="${dealUrl}" target="_blank">Открыть</a>
                    <button>${owned ? "В избранное всё равно" : "В избранное"}</button>
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
                showError(`Ошибка сохранения избранного: ${error.message}`);
            }
        });

        dealsGrid.appendChild(card);
    });
}

async function loadDeals(extra = {}) {
    showError("");
    dealsGrid.innerHTML = "<p>Загрузка...</p>";

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
        dealsCount.textContent = "0 найдено";
        showError(`Ошибка загрузки скидок: ${error.message}`);
        console.error(error);
    }
}

async function loadFavorites() {
    try {
        const favorites = await api("/api/favorites");
        favoritesGrid.innerHTML = "";

        if (!favorites.length) {
            favoritesGrid.innerHTML = "<p class='empty-state'>Избранных игр пока нет.</p>";
            return;
        }

        favorites.forEach(fav => {
            const card = document.createElement("article");
            card.className = "card";

            card.innerHTML = `
                <div class="card-body">
                    <h3>${fav.title}</h3>

                    <div class="meta">
                        <div>Магазин: ${fav.store_name}</div>
                        <div>Цена: <s>${money(fav.normal_price)}</s> → <span class="price">${money(fav.sale_price)}</span></div>
                        <div class="discount">Скидка: ${Number(fav.savings || 0).toFixed(2)}%</div>
                        <div>Target price: ${fav.target_price ? money(fav.target_price) : "not set"}</div>
                    </div>

                    <div class="card-actions">
                        <a href="${fav.deal_url}" target="_blank">Открыть</a>
                        <button>Удалить</button>
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
        showError(`Ошибка загрузки избранного: ${error.message}`);
    }
}

async function loadOwnedGames() {
    try {
        const games = await api("/api/owned-games");
        ownedGrid.innerHTML = "";
        ownedCount.textContent = `${games.length} игр`;

        if (!games.length) {
            ownedGrid.innerHTML = "<p class='empty-state'>Купленных игр пока нет.</p>";
            return;
        }

        games.forEach(game => {
            const card = document.createElement("article");
            card.className = "card";

            card.innerHTML = `
                <div class="card-body">
                    <span class="owned-badge">Уже куплено</span>
                    <h3>${game.title || game.platform_game_id}</h3>
                    <div class="meta">
                        <div>Платформа: ${game.platform}</div>
                        <div>ID: ${game.platform_game_id}</div>
                        <div>Playtime: ${game.playtime_minutes || 0} min</div>
                    </div>
                    <div class="card-actions">
                        <button>Удалить</button>
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
        showError(`Ошибка загрузки библиотеки: ${error.message}`);
    }
}

async function addManualOwnedGame() {
    const platform = document.getElementById("manualPlatform").value;
    const title = document.getElementById("manualTitle").value.trim();
    const platformGameId = document.getElementById("manualGameId").value.trim();

    if (!title) {
        showError("Введи название игры.");
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
        showError(`Ошибка добавления игры: ${error.message}`);
    }
}

async function syncSteamLibrary() {
    const steamId = document.getElementById("steamIdInput").value.trim();

    if (!steamId) {
        showError("Введи SteamID64.");
        return;
    }

    steamSyncStatus.textContent = "Синхронизация...";
    showError("");

    try {
        const result = await api("/api/steam/sync", {
            method: "POST",
            body: JSON.stringify({ steam_id: steamId })
        });

        steamSyncStatus.textContent = `Готово. Синхронизировано игр: ${result.games_count}`;
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

document.getElementById("loadDealsBtn").addEventListener("click", () => loadDeals());
document.getElementById("sortSelect").addEventListener("change", () => renderDeals(lastDeals));
document.getElementById("hideOwned").addEventListener("change", () => loadDeals());
document.getElementById("manualAddBtn").addEventListener("click", addManualOwnedGame);
document.getElementById("syncSteamBtn").addEventListener("click", syncSteamLibrary);

document.querySelectorAll("[data-preset]").forEach(button => {
    button.addEventListener("click", () => applyPreset(button.dataset.preset));
});

document.getElementById("titleSearch").addEventListener("keydown", event => {
    if (event.key === "Enter") {
        loadDeals();
    }
});

(async function init() {
    setupSupportModal();
    await loadStores();
    await loadDeals();
    await loadFavorites();
    await loadOwnedGames();
})();
