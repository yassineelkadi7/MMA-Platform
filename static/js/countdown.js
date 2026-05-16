/**
 * countdown.js — Vanilla JS countdown widget for MMA Fighting Platform.
 *
 * Polls /events/api/countdown/ every second.
 * - Displays days, hours, minutes, seconds remaining.
 * - When seconds_remaining reaches 0, shows "Event is live!" and re-polls after 30s.
 * - If event_id is null, shows "No upcoming events".
 */
(function () {
  "use strict";

  var COUNTDOWN_URL = "/events/api/countdown/";
  var POLL_INTERVAL_MS = 1000;      // normal polling: every 1 second
  var LIVE_REPOLL_MS = 30000;       // re-poll after 30s when event is live

  var timerId = null;
  var lastData = null;              // last API response
  var localSecondsRemaining = 0;   // client-side countdown between polls

  // DOM element references (resolved once on init)
  var elDays, elHours, elMinutes, elSeconds, elEventName, elDisplay;

  function init() {
    elDisplay = document.getElementById("countdown-display");
    if (!elDisplay) return;

    elDays = document.getElementById("countdown-days");
    elHours = document.getElementById("countdown-hours");
    elMinutes = document.getElementById("countdown-minutes");
    elSeconds = document.getElementById("countdown-seconds");
    elEventName = document.getElementById("countdown-event-name");

    fetchAndSchedule();
  }

  /**
   * Fetch fresh data from the API, update state, then schedule the next tick.
   */
  function fetchAndSchedule() {
    fetch(COUNTDOWN_URL)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        lastData = data;
        localSecondsRemaining = data.seconds_remaining || 0;
        render();
        scheduleNextTick();
      })
      .catch(function (err) {
        console.error("Countdown fetch error:", err);
        // Retry after the normal interval even on error
        timerId = setTimeout(fetchAndSchedule, POLL_INTERVAL_MS);
      });
  }

  /**
   * Decide when to fire the next update.
   * - If no event or event is live: re-fetch from API after LIVE_REPOLL_MS.
   * - Otherwise: decrement locally every second, re-fetch when we hit 0.
   */
  function scheduleNextTick() {
    clearTimeout(timerId);

    if (!lastData || lastData.event_id === null) {
      // No upcoming event — no need to tick rapidly
      return;
    }

    if (localSecondsRemaining <= 0) {
      // Event just went live — re-poll after 30s
      timerId = setTimeout(fetchAndSchedule, LIVE_REPOLL_MS);
      return;
    }

    // Decrement locally each second for smooth display
    timerId = setTimeout(function () {
      localSecondsRemaining -= 1;
      render();
      scheduleNextTick();
    }, POLL_INTERVAL_MS);
  }

  /**
   * Update the DOM based on current state.
   */
  function render() {
    if (!elDisplay) return;

    // No event case
    if (!lastData || lastData.event_id === null) {
      showMessage("No upcoming events");
      return;
    }

    // Live case
    if (localSecondsRemaining <= 0) {
      showMessage("Event is live!");
      if (elEventName) {
        elEventName.textContent = lastData.name || "";
      }
      return;
    }

    // Normal countdown
    var total = localSecondsRemaining;
    var days = Math.floor(total / 86400);
    var hours = Math.floor((total % 86400) / 3600);
    var minutes = Math.floor((total % 3600) / 60);
    var seconds = total % 60;

    if (elDays) elDays.textContent = String(days).padStart(2, "0");
    if (elHours) elHours.textContent = String(hours).padStart(2, "0");
    if (elMinutes) elMinutes.textContent = String(minutes).padStart(2, "0");
    if (elSeconds) elSeconds.textContent = String(seconds).padStart(2, "0");

    if (elEventName && lastData.name) {
      elEventName.textContent = lastData.name;
    }

    // Restore the digit display if it was replaced by a message
    restoreDigitDisplay();
  }

  /**
   * Replace the digit display with a plain text message.
   */
  function showMessage(msg) {
    var msgEl = elDisplay.querySelector(".countdown-message");
    if (!msgEl) {
      // Hide digit elements
      var digits = elDisplay.querySelectorAll(
        ".countdown-unit, .countdown-separator"
      );
      digits.forEach(function (el) {
        el.style.display = "none";
      });
      // Create message element
      msgEl = document.createElement("p");
      msgEl.className = "countdown-message fw-bold fs-4 text-primary mb-0";
      elDisplay.insertBefore(msgEl, elDisplay.firstChild);
    }
    msgEl.textContent = msg;
  }

  /**
   * Remove the message overlay and restore digit elements.
   */
  function restoreDigitDisplay() {
    var msgEl = elDisplay.querySelector(".countdown-message");
    if (msgEl) {
      msgEl.remove();
      var digits = elDisplay.querySelectorAll(
        ".countdown-unit, .countdown-separator"
      );
      digits.forEach(function (el) {
        el.style.display = "";
      });
    }
  }

  // Initialise once the DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
