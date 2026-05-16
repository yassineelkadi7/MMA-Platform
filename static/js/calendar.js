/**
 * calendar.js — Improved month grid calendar for MMA Fighting Platform.
 *
 * Features:
 * - Larger cells with proper spacing
 * - Event cards with status colour coding (upcoming=blue, live=red, completed=grey)
 * - Today highlighted with a filled circle
 * - Smooth hover effects
 * - Event count badge when multiple events on same day
 * - Responsive: collapses to compact view on small screens
 */
(function () {
  "use strict";

  const DAY_NAMES   = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const MONTH_NAMES = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December",
  ];

  // Status → Bootstrap colour class
  const STATUS_COLORS = {
    upcoming:  "bg-primary",
    live:      "bg-danger",
    completed: "bg-secondary",
    cancelled: "bg-warning text-dark",
  };

  let allEvents   = [];
  let currentYear, currentMonth;

  /* ── Init ── */
  function init() {
    const container = document.getElementById("calendar-container");
    if (!container) return;

    const eventsUrl = container.dataset.eventsUrl || "/events/api/calendar/";
    const now = new Date();
    currentYear  = now.getFullYear();
    currentMonth = now.getMonth();

    // Inject styles
    injectStyles();

    // Show loading spinner
    container.innerHTML = '<div class="d-flex justify-content-center align-items-center py-5">' +
      '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading…</span></div></div>';

    fetch(eventsUrl)
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(data => { allEvents = Array.isArray(data) ? data : []; renderCalendar(); })
      .catch(err => {
        container.innerHTML = '<div class="alert alert-warning m-3">Could not load events. Please try again later.</div>';
      });

    // Navigation
    document.getElementById("cal-prev")?.addEventListener("click", () => {
      currentMonth--;
      if (currentMonth < 0) { currentMonth = 11; currentYear--; }
      renderCalendar();
    });
    document.getElementById("cal-next")?.addEventListener("click", () => {
      currentMonth++;
      if (currentMonth > 11) { currentMonth = 0; currentYear++; }
      renderCalendar();
    });

    // "Today" button
    const todayBtn = document.getElementById("cal-today");
    if (todayBtn) {
      todayBtn.addEventListener("click", () => {
        const now = new Date();
        currentYear  = now.getFullYear();
        currentMonth = now.getMonth();
        renderCalendar();
      });
    }
  }

  /* ── Build date → events map ── */
  function buildEventMap(year, month) {
    const map = {};
    allEvents.forEach(evt => {
      const d = new Date(evt.date);
      if (d.getFullYear() === year && d.getMonth() === month) {
        const key = dateKey(d);
        if (!map[key]) map[key] = [];
        map[key].push(evt);
      }
    });
    return map;
  }

  function dateKey(d) {
    return d.getFullYear() + "-" +
      String(d.getMonth() + 1).padStart(2, "0") + "-" +
      String(d.getDate()).padStart(2, "0");
  }

  /* ── Render ── */
  function renderCalendar() {
    const container = document.getElementById("calendar-container");
    const titleEl   = document.getElementById("cal-title");
    if (!container) return;

    if (titleEl) titleEl.textContent = MONTH_NAMES[currentMonth] + " " + currentYear;

    const eventMap     = buildEventMap(currentYear, currentMonth);
    const today        = new Date();
    const todayStr     = dateKey(today);
    const daysInMonth  = new Date(currentYear, currentMonth + 1, 0).getDate();
    const daysInPrev   = new Date(currentYear, currentMonth, 0).getDate();

    // Monday-first: getDay() returns 0=Sun, so shift
    let firstDayRaw = new Date(currentYear, currentMonth, 1).getDay();
    let firstDay    = (firstDayRaw === 0) ? 6 : firstDayRaw - 1; // 0=Mon … 6=Sun

    let html = '<div class="cal-grid">';

    // Day-of-week headers
    DAY_NAMES.forEach(name => {
      html += `<div class="cal-header">${name}</div>`;
    });

    // Leading cells (prev month)
    for (let i = 0; i < firstDay; i++) {
      const n = daysInPrev - firstDay + 1 + i;
      html += `<div class="cal-cell other-month"><span class="cal-num">${n}</span></div>`;
    }

    // Current month cells
    for (let day = 1; day <= daysInMonth; day++) {
      const key      = currentYear + "-" + String(currentMonth + 1).padStart(2, "0") + "-" + String(day).padStart(2, "0");
      const isToday  = key === todayStr;
      const isPast   = key < todayStr;
      const dayEvts  = eventMap[key] || [];

      html += `<div class="cal-cell${isToday ? " cal-today" : ""}${isPast ? " cal-past" : ""}">`;
      html += `<span class="cal-num${isToday ? " cal-num-today" : ""}">${day}</span>`;

      // Show up to 2 events, then a "+N more" badge
      const visible = dayEvts.slice(0, 2);
      const extra   = dayEvts.length - visible.length;

      visible.forEach(evt => {
        const colorClass = STATUS_COLORS[evt.status] || "bg-primary";
        const time = new Date(evt.date).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Paris" });
        html += `<a href="/events/${evt.id}/" class="cal-event ${colorClass}" title="${esc(evt.name)} — ${esc(evt.location || "")}">` +
          `<span class="cal-event-time">${time}</span> ${esc(evt.name)}</a>`;
      });

      if (extra > 0) {
        html += `<span class="cal-more">+${extra} more</span>`;
      }

      html += `</div>`;
    }

    // Trailing cells (next month)
    const totalCells   = firstDay + daysInMonth;
    const trailingCells = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
    for (let j = 1; j <= trailingCells; j++) {
      html += `<div class="cal-cell other-month"><span class="cal-num">${j}</span></div>`;
    }

    html += "</div>"; // .cal-grid

    // Event legend
    html += `<div class="cal-legend mt-3 d-flex flex-wrap gap-3">
      <span class="cal-legend-item"><span class="cal-legend-dot bg-primary"></span> Upcoming</span>
      <span class="cal-legend-item"><span class="cal-legend-dot bg-danger"></span> Live</span>
      <span class="cal-legend-item"><span class="cal-legend-dot bg-secondary"></span> Completed</span>
      <span class="cal-legend-item"><span class="cal-legend-dot bg-warning"></span> Cancelled</span>
    </div>`;

    container.innerHTML = html;
  }

  /* ── Inject CSS ── */
  function injectStyles() {
    if (document.getElementById("cal-styles")) return;
    const style = document.createElement("style");
    style.id = "cal-styles";
    style.textContent = `
      .cal-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 3px;
        background: var(--bs-border-color, #dee2e6);
        border: 1px solid var(--bs-border-color, #dee2e6);
        border-radius: 0.5rem;
        overflow: hidden;
      }
      .cal-header {
        background: #1a1a2e;
        color: #fff;
        text-align: center;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.6rem 0.25rem;
      }
      .cal-cell {
        background: var(--bs-body-bg, #fff);
        min-height: 100px;
        padding: 0.4rem 0.5rem;
        display: flex;
        flex-direction: column;
        gap: 3px;
        transition: background 0.15s;
        position: relative;
      }
      .cal-cell:hover {
        background: var(--bs-secondary-bg, #f8f9fa);
      }
      .cal-cell.other-month {
        background: var(--bs-tertiary-bg, #f1f3f5);
        opacity: 0.55;
      }
      .cal-cell.cal-past {
        opacity: 0.75;
      }
      .cal-cell.cal-today {
        background: #e8f0fe;
        box-shadow: inset 0 0 0 2px #0d6efd;
      }
      [data-bs-theme="dark"] .cal-cell.cal-today {
        background: #1a2a4a;
      }
      .cal-num {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--bs-secondary-color, #6c757d);
        line-height: 1;
        margin-bottom: 2px;
      }
      .cal-num-today {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: #0d6efd;
        color: #fff !important;
        border-radius: 50%;
        font-size: 0.75rem;
      }
      .cal-event {
        display: block;
        font-size: 0.68rem;
        font-weight: 500;
        color: #fff !important;
        text-decoration: none;
        border-radius: 4px;
        padding: 2px 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.4;
        transition: opacity 0.15s, transform 0.1s;
      }
      .cal-event:hover {
        opacity: 0.85;
        transform: translateY(-1px);
      }
      .cal-event-time {
        opacity: 0.8;
        font-size: 0.6rem;
        margin-right: 2px;
      }
      .cal-more {
        font-size: 0.65rem;
        color: var(--bs-secondary-color, #6c757d);
        font-weight: 600;
        padding: 1px 4px;
        cursor: default;
      }
      .cal-legend {
        font-size: 0.78rem;
        color: var(--bs-secondary-color, #6c757d);
      }
      .cal-legend-item {
        display: inline-flex;
        align-items: center;
        gap: 5px;
      }
      .cal-legend-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
      }
      @media (max-width: 576px) {
        .cal-cell { min-height: 60px; padding: 0.25rem; }
        .cal-event { font-size: 0.6rem; padding: 1px 3px; }
        .cal-event-time { display: none; }
        .cal-header { font-size: 0.65rem; padding: 0.4rem 0.1rem; }
      }
    `;
    document.head.appendChild(style);
  }

  function esc(str) {
    return String(str)
      .replace(/&/g,"&amp;").replace(/</g,"&lt;")
      .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
