/**
 * Digirary - Client JavaScript
 * Lightweight, zero-dependency interactivity.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const searchInput = document.getElementById("bookSearchInput");
    const clearSearchBtn = document.getElementById("clearSearchBtn");
    const categoryPills = document.querySelectorAll(".genre-pill");
    const booksGrid = document.getElementById("booksGrid");
    const noResultsState = document.getElementById("noResultsState");
    const resultsCount = document.getElementById("resultsCount");
    const resetSearchFilterBtn = document.getElementById("resetSearchFilterBtn");
    const mobileNavToggle = document.getElementById("mobileNavToggle");
    const mainNav = document.getElementById("main-nav");

    // Modal Elements
    const modalOverlay = document.getElementById("bookModalOverlay");
    const modalCloseBtn = document.getElementById("modalCloseBtn");
    const modalBody = document.getElementById("modalBody");

    let currentCategory = "all";
    let searchDebounceTimer = null;

    // Mobile Nav Toggle
    if (mobileNavToggle && mainNav) {
        mobileNavToggle.addEventListener("click", () => {
            mainNav.classList.toggle("mobile-active");
        });
    }

    // Attach book card click listeners for initially rendered items
    attachCardListeners();

    // Auto-dismiss Flash Messages after 6 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // Search Input Event
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const val = e.target.value.trim();
            if (clearSearchBtn) {
                clearSearchBtn.style.display = val.length > 0 ? "flex" : "none";
            }

            clearTimeout(searchDebounceTimer);
            searchDebounceTimer = setTimeout(() => {
                filterBooks(val, currentCategory);
            }, 250);
        });
    }

    // Clear Search Button Event
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener("click", () => {
            searchInput.value = "";
            clearSearchBtn.style.display = "none";
            searchInput.focus();
            filterBooks("", currentCategory);
        });
    }

    // Category Pill Filter Buttons
    categoryPills.forEach((pill) => {
        pill.addEventListener("click", (e) => {
            // Only intercept if on home page with AJAX grid
            if (booksGrid && pill.getAttribute("data-category")) {
                e.preventDefault();
                categoryPills.forEach((p) => p.classList.remove("active"));
                pill.classList.add("active");
                currentCategory = pill.getAttribute("data-category");
                const query = searchInput ? searchInput.value.trim() : "";
                filterBooks(query, currentCategory);
            }
        });
    });

    // Reset Filters Button
    if (resetSearchFilterBtn) {
        resetSearchFilterBtn.addEventListener("click", () => {
            if (searchInput) searchInput.value = "";
            if (clearSearchBtn) clearSearchBtn.style.display = "none";
            currentCategory = "all";
            categoryPills.forEach((p) => {
                if (p.getAttribute("data-category") === "all") {
                    p.classList.add("active");
                } else {
                    p.classList.remove("active");
                }
            });
            filterBooks("", "all");
        });
    }

    // Fetch and Filter Books via API
    async function filterBooks(query, category) {
        try {
            const url = new URL("/api/books", window.location.origin);
            if (query) url.searchParams.set("search", query);
            if (category && category !== "all") url.searchParams.set("category", category);

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                renderBooks(data.books);
            }
        } catch (err) {
            console.error("Error fetching filtered books:", err);
        }
    }

    // Render Books Grid
    function renderBooks(books) {
        if (!booksGrid) return;

        if (books.length === 0) {
            booksGrid.innerHTML = "";
            if (noResultsState) noResultsState.style.display = "block";
            if (resultsCount) resultsCount.textContent = "0 books found";
            return;
        }

        if (noResultsState) noResultsState.style.display = "none";
        if (resultsCount) resultsCount.textContent = `Showing ${books.length} book${books.length > 1 ? "s" : ""}`;

        const html = books
            .map((b) => {
                const availabilityBadge = b.available
                    ? '<span class="badge-status-available">Available</span>'
                    : '<span class="badge-status-borrowed">Borrowed</span>';

                const borrowBtn = b.available
                    ? `<a href="/books/${b.id}/borrow" class="btn btn-primary btn-xs">Borrow</a>`
                    : `<button class="btn btn-secondary btn-xs" disabled>Checked Out</button>`;

                return `
                <article class="book-card" data-id="${b.id}" data-category="${b.category_slug}">
                    <div class="book-cover" style="background: ${b.cover_gradient};">
                        <div class="book-spine-effect"></div>
                        <div class="book-cover-meta">
                            <span class="book-category-tag">${escapeHtml(b.category_name)}</span>
                            ${availabilityBadge}
                        </div>
                        <h3 class="book-cover-title">${escapeHtml(b.title)}</h3>
                        <p class="book-cover-author">By ${escapeHtml(b.author)}</p>
                        <div class="book-cover-footer">
                            <div class="book-rating">
                                <svg viewBox="0 0 24 24" width="14" height="14" fill="#fbbf24" stroke="#fbbf24">
                                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                                </svg>
                                <span>${b.rating}</span>
                            </div>
                            <span class="book-year">${b.published_year}</span>
                        </div>
                    </div>
                    <div class="book-content">
                        <p class="book-summary">${escapeHtml(b.summary)}</p>
                        <div class="book-footer">
                            <span class="book-pages-badge">
                                <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2" fill="none">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                </svg>
                                ${b.total_pages} pages
                            </span>
                            <div class="card-btn-group">
                                <a href="/books/${b.id}" class="btn-card-action">Details</a>
                                ${borrowBtn}
                            </div>
                        </div>
                    </div>
                </article>
            `;
            })
            .join("");

        booksGrid.innerHTML = html;
        attachCardListeners();
    }

    // Attach Click Events to Book Cards & Details Buttons
    function attachCardListeners() {
        const viewButtons = document.querySelectorAll(".view-book-btn");
        viewButtons.forEach((btn) => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const bookId = btn.getAttribute("data-id");
                openBookModal(bookId);
            });
        });
    }

    // Open Book Details Modal
    async function openBookModal(bookId) {
        if (!modalOverlay || !modalBody) return;

        try {
            const res = await fetch(`/api/books/${bookId}`);
            const data = await res.json();

            if (!data.success || !data.book) return;

            const b = data.book;

            const borrowBtnHtml = b.available
                ? `<a href="/books/${b.id}/borrow" class="btn btn-primary btn-sm">Borrow Book</a>`
                : `<button class="btn btn-secondary btn-sm" disabled>Currently Checked Out</button>`;

            modalBody.innerHTML = `
                <div class="modal-book-header" style="background: ${b.cover_gradient};">
                    <h2 class="modal-book-title">${escapeHtml(b.title)}</h2>
                </div>
                <div class="modal-book-body">
                    <div class="modal-meta-row">
                        <span class="modal-meta-pill" style="color: #60a5fa;">Author: ${escapeHtml(b.author)}</span>
                        <span class="modal-meta-pill">Category: ${escapeHtml(b.category_name)}</span>
                        <span class="modal-meta-pill">Rating: ★ ${b.rating}</span>
                        <span class="modal-meta-pill">${b.available ? "✅ Available" : "⏳ Checked Out"}</span>
                    </div>

                    <h4 style="font-size: 1rem; margin-bottom: 8px; color: #f1f5f9;">Overview & Synopsis</h4>
                    <p class="modal-summary-text">${escapeHtml(b.summary)}</p>

                    <div class="modal-info-table">
                        <div>
                            <div class="modal-info-label">Publication Year</div>
                            <div class="modal-info-value">${b.published_year || "N/A"}</div>
                        </div>
                        <div>
                            <div class="modal-info-label">Page Count</div>
                            <div class="modal-info-value">${b.total_pages} pages</div>
                        </div>
                        <div>
                            <div class="modal-info-label">ISBN Reference</div>
                            <div class="modal-info-value">${escapeHtml(b.isbn || "N/A")}</div>
                        </div>
                        <div>
                            <div class="modal-info-label">Storage Engine</div>
                            <div class="modal-info-value">SQLite3 Local</div>
                        </div>
                    </div>

                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px;">
                        <a href="/books/${b.id}" class="btn-card-action">Full Book Page &rarr;</a>
                        <div style="display: flex; gap: 10px;">
                            ${borrowBtnHtml}
                            <button class="btn btn-secondary btn-sm" id="closeModalActionBtn">Close</button>
                        </div>
                    </div>
                </div>
            `;

            modalOverlay.classList.add("active");
            document.body.style.overflow = "hidden";

            const closeActionBtn = document.getElementById("closeModalActionBtn");
            if (closeActionBtn) {
                closeActionBtn.addEventListener("click", closeModal);
            }
        } catch (err) {
            console.error("Failed to load book details:", err);
        }
    }

    function closeModal() {
        if (!modalOverlay) return;
        modalOverlay.classList.remove("active");
        document.body.style.overflow = "";
    }

    if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);

    if (modalOverlay) {
        modalOverlay.addEventListener("click", (e) => {
            if (e.target === modalOverlay) closeModal();
        });
    }

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modalOverlay && modalOverlay.classList.contains("active")) {
            closeModal();
        }
    });

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
