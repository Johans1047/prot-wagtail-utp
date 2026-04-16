(function () {
    "use strict";

    var FILTER_ALL = "all";
    var FILTER_UNCLASSIFIED = "unclassified";
    var DEFAULT_PAGE_SIZE = 24;
    var RENDER_DEBOUNCE_MS = 80;

    function normalizeText(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim();
    }

    function normalizeYear(value) {
        var raw = String(value || "").trim();
        if (/^\d{4}$/.test(raw)) {
            return raw;
        }
        return "";
    }

    function isGallerySnippetEditView() {
        return /\/snippets\/web\/gallery\/edit\/\d+\/?$/.test(window.location.pathname || "");
    }

    function extractRouteInfo() {
        var pathname = window.location.pathname || "";
        var match = pathname.match(/^(.*\/snippets\/web\/gallery\/)edit\/(\d+)\/?$/);
        if (!match) {
            return null;
        }
        return {
            galleryId: match[2],
            endpoint: match[1] + "images-data/" + match[2] + "/",
        };
    }

    function findGalleryPanel() {
        var formsRootById = document.getElementById("id_gallery_images-FORMS");
        if (formsRootById) {
            var rootNode = formsRootById;
            while (rootNode && rootNode !== document.body) {
                if (
                    rootNode.querySelector &&
                    rootNode.querySelector("#id_gallery_images-FORMS") &&
                    rootNode.querySelector("#id_gallery_images-ADD")
                ) {
                    return rootNode;
                }
                rootNode = rootNode.parentElement;
            }

            return formsRootById.parentElement || formsRootById;
        }

        var yearInput = document.querySelector('input[name*="gallery_images"][name$="-year"]');

        if (yearInput) {
            var inlinePanel = yearInput.closest("[data-inline-panel]");
            if (inlinePanel) {
                return inlinePanel;
            }

            var legacyPanel = yearInput.closest(".w-inline-panel");
            if (legacyPanel) {
                return legacyPanel;
            }

            var node = yearInput;
            while (node && node !== document.body) {
                if (
                    node.querySelector &&
                    node.querySelector('input[name*="gallery_images"][name$="-year"]') &&
                    (node.querySelector("#id_gallery_images-ADD") || node.querySelector('[id="id_gallery_images-FORMS"]'))
                ) {
                    return node;
                }
                node = node.parentElement;
            }
        }

        var candidates = document.querySelectorAll("section, div, form");
        for (var i = 0; i < candidates.length; i += 1) {
            var candidate = candidates[i];
            if (
                candidate.querySelector &&
                candidate.querySelector('input[name*="gallery_images"][name$="-year"]') &&
                (candidate.querySelector("#id_gallery_images-ADD") || candidate.querySelector('[id="id_gallery_images-FORMS"]'))
            ) {
                return candidate;
            }
        }

        return null;
    }

    function findItemRoot(inputEl) {
        if (!inputEl) {
            return null;
        }
        return (
            inputEl.closest("[data-inline-panel-child]") ||
            inputEl.closest(".sequence-member") ||
            inputEl.closest("li") ||
            inputEl.closest(".w-panel") ||
            inputEl.parentElement
        );
    }

    function getRowId(row) {
        var idInput = row.querySelector('input[name*="gallery_images"][name$="-id"]');
        return idInput && idInput.value ? String(idInput.value).trim() : "";
    }

    function getRowYear(row) {
        var yearInput = row.querySelector('input[name*="gallery_images"][name$="-year"]');
        return normalizeYear(yearInput ? yearInput.value : "");
    }

    function isDeletedRow(row) {
        var deleteInput = row.querySelector('input[name*="gallery_images"][name$="-DELETE"]');
        return !!(deleteInput && deleteInput.checked);
    }

    function expandPanelWidth(panel) {
        panel.classList.add("gallery-admin-full-width");

        var node = panel.parentElement;
        while (node && node !== document.body) {
            if (
                node.classList && (
                    node.classList.contains("w-panel__content") ||
                    node.classList.contains("w-panel--nested") ||
                    node.classList.contains("w-form-width") ||
                    node.classList.contains("nice-padding")
                )
            ) {
                node.classList.add("gallery-admin-full-width");
            }
            node = node.parentElement;
        }
    }

    function scheduleRender(state, includeChips) {
        if (includeChips) {
            state.pendingChipsRender = true;
        }

        if (state.renderTimer) {
            return;
        }

        state.renderTimer = window.setTimeout(function () {
            state.renderTimer = null;
            var mustRenderChips = state.pendingChipsRender;
            state.pendingChipsRender = false;

            window.requestAnimationFrame(function () {
                if (mustRenderChips) {
                    renderFilterChips(state);
                }
                renderRows(state);
            });
        }, RENDER_DEBOUNCE_MS);
    }

    function ensureStyles() {
        if (document.getElementById("gallery-admin-enhancements-style")) {
            return;
        }

        var style = document.createElement("style");
        style.id = "gallery-admin-enhancements-style";
        style.textContent = ""
            + ".gallery-admin-full-width{max-width:none !important;width:100% !important;}"
            + "#id_gallery_images-FORMS,#gallery-admin-toolbar,#gallery-admin-grid-root{width:100%;max-width:none;}"
            + "#id_gallery_images-FORMS{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;align-items:start;}"
            + "#id_gallery_images-FORMS > [data-inline-panel-child]{min-width:0;}"
            + "#gallery-admin-toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin:0 0 16px 0;padding:12px;border:1px solid var(--w-color-border-field,rgba(0,0,0,.15));border-radius:10px;background:var(--w-color-surface-field,#fff);color:var(--w-color-text-label,#1f1f1f);}" 
            + "#gallery-admin-filter-group{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}"
            + "#gallery-admin-filter-chips{display:flex;flex-wrap:wrap;gap:8px;}"
            + ".gallery-filter-chip{border:1px solid var(--w-color-border-field,rgba(0,0,0,.2));background:var(--w-color-surface-page,#fff);color:var(--w-color-text-label,#222);border-radius:999px;padding:5px 10px;font-size:12px;font-weight:600;cursor:pointer;}"
            + ".gallery-filter-chip.is-active{background:var(--w-color-primary,#0a5ec2);color:#fff;border-color:var(--w-color-primary,#0a5ec2);}"
            + "#gallery-admin-grid-root{display:flex;flex-direction:column;gap:20px;margin-bottom:12px;}"
            + ".gallery-year-section{border:1px solid var(--w-color-border-field,rgba(0,0,0,.12));border-radius:12px;padding:12px;background:var(--w-color-surface-field,#fff);color:var(--w-color-text-label,#1f1f1f);}" 
            + ".gallery-year-heading{font-size:15px;font-weight:700;margin:0 0 10px 0;}"
            + ".gallery-year-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;align-items:start;}"
            + ".gallery-admin-card{margin:0 !important;border:1px solid var(--w-color-border-field,rgba(0,0,0,.12));border-radius:10px;padding:10px;background:var(--w-color-surface-page,#fff);color:var(--w-color-text-label,#1f1f1f);width:100%;box-sizing:border-box;}" 
            + "#gallery-admin-pagination{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end;}"
            + ".gallery-page-btn{border:1px solid var(--w-color-border-field,rgba(0,0,0,.2));background:var(--w-color-surface-page,#fff);color:var(--w-color-text-label,#222);border-radius:6px;padding:4px 8px;cursor:pointer;}"
            + ".gallery-page-btn[disabled]{opacity:.5;cursor:not-allowed;}"
            + "#gallery-admin-page-info{font-size:12px;color:var(--w-color-text-meta,#666);}"
            + "@media (min-width: 1800px){.gallery-year-grid{grid-template-columns:repeat(auto-fill,minmax(280px,1fr));}}";
        document.head.appendChild(style);
    }

    function collectRows(panel) {
        var inputs = Array.prototype.slice.call(
            panel.querySelectorAll('input[name*="gallery_images"][name$="-year"]')
        );
        var seen = new Set();
        var rows = [];

        inputs.forEach(function (input) {
            if (!input || input.name.indexOf("__prefix__") !== -1 || input.closest("template")) {
                return;
            }

            var row = findItemRoot(input);
            if (!row || seen.has(row)) {
                return;
            }
            seen.add(row);
            rows.push(row);
        });

        return rows;
    }

    function findAddButton(panel) {
        var byId = document.getElementById("id_gallery_images-ADD") || panel.querySelector("#id_gallery_images-ADD");
        if (byId) {
            return byId;
        }

        var candidates = Array.prototype.slice.call(panel.querySelectorAll(".w-inline-panel__add-button"));
        for (var i = 0; i < candidates.length; i += 1) {
            if (!candidates[i].closest("#gallery-admin-toolbar")) {
                return candidates[i];
            }
        }

        if (candidates.length > 0) {
            return candidates[0];
        }

        return Array.prototype.slice.call(panel.querySelectorAll("button, a")).find(function (el) {
            var txt = normalizeText(el.textContent);
            return txt.indexOf("anadir") !== -1 && txt.indexOf("imagen") !== -1;
        }) || null;
    }

    function ensureTopAddButton(panel, toolbar) {
        var addButton = findAddButton(panel);
        if (!addButton) {
            return;
        }

        if (!addButton.closest("#gallery-admin-toolbar")) {
            addButton.dataset.galleryTopAdd = "1";
            addButton.style.margin = "0";
            toolbar.appendChild(addButton);
        }

        var extraButtons = Array.prototype.slice.call(panel.querySelectorAll(".w-inline-panel__add-button"));
        extraButtons.forEach(function (button) {
            if (!button.closest("#gallery-admin-toolbar")) {
                button.style.display = "none";
            }
        });
    }

    function ensurePaginationToolbar(toolbar) {
        var pagination = toolbar.querySelector("#gallery-admin-pagination");
        if (pagination) {
            return pagination;
        }

        pagination = document.createElement("div");
        pagination.id = "gallery-admin-pagination";

        var prev = document.createElement("button");
        prev.type = "button";
        prev.id = "gallery-admin-prev-page";
        prev.className = "gallery-page-btn";
        prev.textContent = "Anterior";

        var info = document.createElement("span");
        info.id = "gallery-admin-page-info";
        info.textContent = "Página 1 de 1";

        var next = document.createElement("button");
        next.type = "button";
        next.id = "gallery-admin-next-page";
        next.className = "gallery-page-btn";
        next.textContent = "Siguiente";

        pagination.appendChild(prev);
        pagination.appendChild(info);
        pagination.appendChild(next);
        toolbar.appendChild(pagination);

        return pagination;
    }

    function bindPaginationEvents(state) {
        var pagination = ensurePaginationToolbar(state.toolbar);
        if (pagination.dataset.bound === "1") {
            return;
        }

        var prev = pagination.querySelector("#gallery-admin-prev-page");
        var next = pagination.querySelector("#gallery-admin-next-page");

        if (prev) {
            prev.addEventListener("click", function () {
                if (state.currentPage <= 1) {
                    return;
                }
                state.currentPage -= 1;
                renderRows(state);
            });
        }

        if (next) {
            next.addEventListener("click", function () {
                if (state.currentPage >= state.totalPages) {
                    return;
                }
                state.currentPage += 1;
                renderRows(state);
            });
        }

        pagination.dataset.bound = "1";
    }

    function bindPanelActionEvents(state) {
        if (state.panel.dataset.galleryActionBound === "1") {
            return;
        }

        state.panel.addEventListener("click", function (event) {
            var target = event.target && event.target.closest ? event.target.closest("button, a") : null;
            if (!target) {
                return;
            }

            if (target.id === "id_gallery_images-ADD") {
                state.pendingFocusNewRow = true;
                if (state.activeFilter !== FILTER_ALL) {
                    state.activeFilter = FILTER_ALL;
                    renderFilterChips(state);
                }
                window.setTimeout(function () {
                    scheduleRender(state, true);
                }, 160);
                return;
            }

            if (target.hasAttribute("data-inline-panel-child-delete")) {
                state.localOrderingMode = true;
                window.setTimeout(function () {
                    scheduleRender(state, true);
                }, 0);
                return;
            }

            if (
                target.hasAttribute("data-inline-panel-child-move-up") ||
                target.hasAttribute("data-inline-panel-child-move-down") ||
                target.hasAttribute("data-inline-panel-child-drag")
            ) {
                state.localOrderingMode = true;
                window.setTimeout(function () {
                    scheduleRender(state, false);
                }, 0);
            }
        });

        state.panel.addEventListener("change", function (event) {
            var target = event.target;
            if (!target || !target.name) {
                return;
            }

            if (target.name.indexOf("gallery_images-") !== -1 && target.name.indexOf("-ORDER") !== -1) {
                state.localOrderingMode = true;
                scheduleRender(state, false);
            }
        });

        state.panel.dataset.galleryActionBound = "1";
    }

    function bindDynamicRowsObserver(state) {
        var formsContainer = state.panel.querySelector("#id_gallery_images-FORMS");
        if (!formsContainer || formsContainer.dataset.galleryRowsObserverBound === "1") {
            return;
        }

        var observer = new MutationObserver(function (mutations) {
            if (state.isRendering) {
                return;
            }

            var hasStructuralChanges = false;
            for (var i = 0; i < mutations.length; i += 1) {
                if (
                    (mutations[i].addedNodes && mutations[i].addedNodes.length > 0) ||
                    (mutations[i].removedNodes && mutations[i].removedNodes.length > 0)
                ) {
                    hasStructuralChanges = true;
                    break;
                }
            }

            if (hasStructuralChanges) {
                state.localOrderingMode = true;
                scheduleRender(state, true);
            }
        });

        observer.observe(formsContainer, { childList: true });
        formsContainer.dataset.galleryRowsObserverBound = "1";
    }

    function updatePaginationControls(state, totalItems) {
        var pagination = ensurePaginationToolbar(state.toolbar);
        var info = pagination.querySelector("#gallery-admin-page-info");
        var prev = pagination.querySelector("#gallery-admin-prev-page");
        var next = pagination.querySelector("#gallery-admin-next-page");

        var totalPages = Math.max(1, Math.ceil(totalItems / state.pageSize));
        if (state.currentPage > totalPages) {
            state.currentPage = totalPages;
        }

        state.totalPages = totalPages;

        if (info) {
            info.textContent = "Página " + state.currentPage + " de " + totalPages + " (" + totalItems + " imágenes)";
        }
        if (prev) {
            prev.disabled = state.currentPage <= 1;
        }
        if (next) {
            next.disabled = state.currentPage >= totalPages;
        }

        pagination.style.display = totalItems > state.pageSize ? "flex" : "none";
    }

    function ensureToolbar(panel) {
        var toolbar = panel.querySelector("#gallery-admin-toolbar");
        if (toolbar) {
            ensurePaginationToolbar(toolbar);
            return toolbar;
        }

        toolbar = document.createElement("div");
        toolbar.id = "gallery-admin-toolbar";

        var filterGroup = document.createElement("div");
        filterGroup.id = "gallery-admin-filter-group";

        var title = document.createElement("strong");
        title.textContent = "Filtrar por año:";

        var chips = document.createElement("div");
        chips.id = "gallery-admin-filter-chips";

        filterGroup.appendChild(title);
        filterGroup.appendChild(chips);
        toolbar.appendChild(filterGroup);

        ensurePaginationToolbar(toolbar);
        panel.insertBefore(toolbar, panel.firstChild);
        ensureTopAddButton(panel, toolbar);

        return toolbar;
    }

    function ensureLayoutContainers(panel) {
        var formsContainer = panel.querySelector("#id_gallery_images-FORMS");

        var root = panel.querySelector("#gallery-admin-grid-root");
        if (!root) {
            root = document.createElement("div");
            root.id = "gallery-admin-grid-root";
            var toolbar = ensureToolbar(panel);
            panel.insertBefore(root, toolbar.nextSibling);
        }

        return { root: root, formsContainer: formsContainer };
    }

    function toIdMap(ids) {
        var map = {};
        (ids || []).forEach(function (idValue) {
            map[String(idValue)] = true;
        });
        return map;
    }

    function matchesFilter(year, activeFilter) {
        if (activeFilter === FILTER_ALL) {
            return true;
        }
        if (activeFilter === FILTER_UNCLASSIFIED) {
            return !year;
        }
        return year === activeFilter;
    }

    function buildOrderedRows(rows, orderedIds) {
        var byId = {};
        var ordered = [];
        var used = new Set();

        rows.forEach(function (row) {
            var rowId = getRowId(row);
            if (rowId) {
                byId[rowId] = row;
            }
        });

        (orderedIds || []).forEach(function (idValue) {
            var key = String(idValue);
            if (byId[key] && !used.has(byId[key])) {
                ordered.push(byId[key]);
                used.add(byId[key]);
            }
        });

        rows.forEach(function (row) {
            if (!used.has(row)) {
                ordered.push(row);
                used.add(row);
            }
        });

        return ordered;
    }

    function attachRowListeners(state, rows) {
        rows.forEach(function (row) {
            var yearInput = row.querySelector('input[name*="gallery_images"][name$="-year"]');
            if (!yearInput || yearInput.dataset.galleryAdminBound === "1") {
                return;
            }

            var rowId = getRowId(row);
            if (rowId && !row.dataset.initialYear) {
                row.dataset.initialYear = getRowYear(row);
            }

            var onYearChange = function () {
                var currentYear = getRowYear(row);
                if (row.dataset.initialYear !== undefined) {
                    row.dataset.yearDirty = row.dataset.initialYear !== currentYear ? "1" : "0";
                }
                scheduleRender(state, false);
            };

            yearInput.addEventListener("change", onYearChange);
            yearInput.addEventListener("input", onYearChange);
            yearInput.dataset.galleryAdminBound = "1";
        });
    }

    function renderFilterChips(state) {
        var chipsRoot = state.toolbar.querySelector("#gallery-admin-filter-chips");
        if (!chipsRoot) {
            return;
        }

        var rows = collectRows(state.panel);
        var hasUnclassifiedLocal = rows.some(function (row) {
            return !getRowYear(row);
        });

        var localYears = rows
            .map(function (row) { return getRowYear(row); })
            .filter(function (yearValue) { return !!yearValue; })
            .filter(function (value, index, arr) { return arr.indexOf(value) === index; })
            .sort(function (a, b) { return Number(b) - Number(a); });

        var yearsSource = (state.availableYears && state.availableYears.length > 0)
            ? state.availableYears
            : localYears;

        var values = [FILTER_ALL].concat((yearsSource || []).map(function (year) {
            return String(year);
        }));

        if (state.hasUnclassifiedServer || hasUnclassifiedLocal) {
            values.push(FILTER_UNCLASSIFIED);
        }

        values = values.filter(function (value, index, arr) {
            return arr.indexOf(value) === index;
        });

        chipsRoot.innerHTML = "";

        values.forEach(function (value) {
            var label = "Todos";
            if (value === FILTER_UNCLASSIFIED) {
                label = "Sin clasificar";
            } else if (value !== FILTER_ALL) {
                label = value;
            }

            var chip = document.createElement("button");
            chip.type = "button";
            chip.className = "gallery-filter-chip" + (state.activeFilter === value ? " is-active" : "");
            chip.setAttribute("aria-pressed", state.activeFilter === value ? "true" : "false");
            chip.textContent = label;
            chip.dataset.yearValue = value;
            chip.addEventListener("click", function () {
                if (state.activeFilter === value) {
                    return;
                }
                state.activeFilter = value;
                state.currentPage = 1;
                renderFilterChips(state);
                renderRows(state);
            });

            chipsRoot.appendChild(chip);
        });
    }

    function renderRows(state) {
        if (state.isRendering) {
            return;
        }

        state.isRendering = true;

        try {
            var rows = collectRows(state.panel);
            var containers = ensureLayoutContainers(state.panel);
            var root = containers.root;
            var formsContainer = containers.formsContainer;
            if (!formsContainer) {
                return;
            }

            ensureTopAddButton(state.panel, state.toolbar);
            attachRowListeners(state, rows);

            var orderedRows = state.localOrderingMode ? rows.slice() : buildOrderedRows(rows, state.orderedIds);
            orderedRows.forEach(function (row) {
                if (row.parentElement !== formsContainer) {
                    formsContainer.appendChild(row);
                }
            });

            var candidates = [];

            orderedRows.forEach(function (row) {
                if (isDeletedRow(row)) {
                    row.style.display = "none";
                    return;
                }

                var rowYear = getRowYear(row);
                var visible = matchesFilter(rowYear, state.activeFilter);

                if (!visible) {
                    row.style.display = "none";
                    return;
                }

                row.style.display = "";
                row.classList.add("gallery-admin-card");
                candidates.push({
                    row: row,
                    key: rowYear || FILTER_UNCLASSIFIED,
                });
            });

            if (state.pendingFocusNewRow) {
                var firstUnsavedVisibleIndex = -1;
                for (var k = 0; k < candidates.length; k += 1) {
                    if (!getRowId(candidates[k].row)) {
                        firstUnsavedVisibleIndex = k;
                        state.rowToFocus = candidates[k].row;
                        break;
                    }
                }

                if (firstUnsavedVisibleIndex !== -1) {
                    state.currentPage = Math.floor(firstUnsavedVisibleIndex / state.pageSize) + 1;
                }

                state.pendingFocusNewRow = false;
            }

            updatePaginationControls(state, candidates.length);

            var start = (state.currentPage - 1) * state.pageSize;
            var end = start + state.pageSize;
            var pageItems = candidates.slice(start, end);
            var pageSet = new Set(pageItems.map(function (item) { return item.row; }));

            orderedRows.forEach(function (row) {
                if (isDeletedRow(row)) {
                    row.style.display = "none";
                    return;
                }

                if (pageSet.has(row)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });

            root.innerHTML = "";

            if (pageItems.length === 0) {
                var empty = document.createElement("p");
                empty.textContent = "No hay imágenes para mostrar con este filtro.";
                root.appendChild(empty);
                return;
            }

            if (state.rowToFocus && pageSet.has(state.rowToFocus)) {
                var nodeToFocus = state.rowToFocus;
                state.rowToFocus = null;
                window.requestAnimationFrame(function () {
                    nodeToFocus.scrollIntoView({ behavior: "smooth", block: "center" });
                    var focusTarget = nodeToFocus.querySelector('input[name*="gallery_images"][name$="-year"], button, a, input, select, textarea');
                    if (focusTarget && typeof focusTarget.focus === "function") {
                        focusTarget.focus();
                    }
                });
            }
        } finally {
            state.isRendering = false;
        }
    }

    function fetchAndRender(state) {
        var requestId = state.requestId + 1;
        state.requestId = requestId;

        var query = new URLSearchParams({ year: FILTER_ALL });
        var url = state.route.endpoint + "?" + query.toString();

        fetch(url, {
            method: "GET",
            credentials: "same-origin",
            headers: {
                Accept: "application/json",
            },
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("No se pudo cargar la galería filtrada desde backend.");
                }
                return response.json();
            })
            .then(function (payload) {
                if (requestId !== state.requestId) {
                    return;
                }

                state.availableYears = payload.available_years || [];
                state.orderedIds = (payload.ordered_ids || []).map(function (idValue) {
                    return String(idValue);
                });
                state.orderedIdMap = toIdMap(state.orderedIds);
                state.hasUnclassifiedServer = (payload.groups || []).some(function (group) {
                    return group && group.key === FILTER_UNCLASSIFIED;
                });

                renderFilterChips(state);
                renderRows(state);
            })
            .catch(function () {
                if (requestId !== state.requestId) {
                    return;
                }

                state.availableYears = [];
                state.orderedIds = [];
                state.orderedIdMap = {};
                state.hasUnclassifiedServer = false;
                renderFilterChips(state);
                renderRows(state);
            });
    }

    function init() {
        if (!isGallerySnippetEditView()) {
            return;
        }

        var route = extractRouteInfo();
        if (!route) {
            return;
        }

        var started = false;

        function tryAttach() {
            if (started) {
                return true;
            }

            var panel = findGalleryPanel();
            if (!panel) {
                return false;
            }

            started = true;
            ensureStyles();
            expandPanelWidth(panel);
            var toolbar = ensureToolbar(panel);
            ensureLayoutContainers(panel);

            var state = {
                panel: panel,
                toolbar: toolbar,
                route: route,
                activeFilter: FILTER_ALL,
                availableYears: [],
                orderedIds: [],
                orderedIdMap: {},
                hasUnclassifiedServer: false,
                requestId: 0,
                isRendering: false,
                pageSize: DEFAULT_PAGE_SIZE,
                currentPage: 1,
                totalPages: 1,
                renderTimer: null,
                pendingChipsRender: false,
                pendingFocusNewRow: false,
                rowToFocus: null,
                localOrderingMode: false,
            };

            bindPaginationEvents(state);
            bindPanelActionEvents(state);
            bindDynamicRowsObserver(state);
            renderFilterChips(state);
            fetchAndRender(state);

            return true;
        }

        if (tryAttach()) {
            return;
        }

        var documentObserver = new MutationObserver(function () {
            if (tryAttach()) {
                documentObserver.disconnect();
            }
        });

        documentObserver.observe(document.body, { childList: true, subtree: true });

        window.setTimeout(function () {
            documentObserver.disconnect();
        }, 60000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}());
