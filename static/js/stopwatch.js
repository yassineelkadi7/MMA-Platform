/**
 * stopwatch.js — Client-side stopwatch for MMA Fighting Platform training sessions.
 *
 * Uses performance.now() for sub-second accuracy.
 * Uses setInterval (every 100 ms) for display updates.
 * Exports start(), stop(), reset(), and formatTime() for Jest testing.
 *
 * Display format: MM:SS.T  (T = tenths of a second)
 * Updates #stopwatch-display in the DOM.
 * No fetch calls — entirely client-side.
 *
 * Requirements: 6.2, 6.3, 6.4, 6.5
 */
(function (global) {
  "use strict";

  /** Timestamp (performance.now()) at which the current run started. */
  var startTime = null;

  /** Accumulated elapsed milliseconds from previous runs (before the last start). */
  var elapsed = 0;

  /** setInterval handle; null when not running. */
  var timerId = null;

  /** Whether the stopwatch is currently counting. */
  var running = false;

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * Start the stopwatch.
   * If already running, this is a no-op.
   */
  function start() {
    if (running) return;
    running = true;
    startTime = performance.now();
    timerId = setInterval(updateDisplay, 100);
  }

  /**
   * Stop (pause) the stopwatch.
   * Retains the current elapsed time so it can be resumed with start().
   * If not running, this is a no-op.
   */
  function stop() {
    if (!running) return;
    running = false;
    elapsed += performance.now() - startTime;
    startTime = null;
    clearInterval(timerId);
    timerId = null;
    // Snap the display to the exact frozen value
    updateDisplay();
  }

  /**
   * Reset the stopwatch.
   * Clears the interval, sets elapsed to 0, and resets the display to "00:00.0".
   * Works whether the stopwatch is running or paused.
   */
  function reset() {
    running = false;
    clearInterval(timerId);
    timerId = null;
    startTime = null;
    elapsed = 0;
    updateDisplay();
  }

  // ---------------------------------------------------------------------------
  // Internal helpers
  // ---------------------------------------------------------------------------

  /**
   * Format a duration in milliseconds as "MM:SS.T".
   *
   * @param {number} ms - Duration in milliseconds (non-negative).
   * @returns {string} Formatted time string, e.g. "01:23.4".
   */
  function formatTime(ms) {
    // Guard against negative values (e.g. clock skew edge cases)
    var totalMs = ms < 0 ? 0 : ms;

    var totalTenths = Math.floor(totalMs / 100);
    var tenths = totalTenths % 10;
    var totalSeconds = Math.floor(totalMs / 1000);
    var seconds = totalSeconds % 60;
    var minutes = Math.floor(totalSeconds / 60);

    // Cap minutes at 99 to keep the MM:SS.T format intact
    if (minutes > 99) minutes = 99;

    return (
      String(minutes).padStart(2, "0") +
      ":" +
      String(seconds).padStart(2, "0") +
      "." +
      String(tenths)
    );
  }

  /**
   * Calculate the current total elapsed milliseconds and push it to the DOM.
   */
  function updateDisplay() {
    var currentElapsed = elapsed;
    if (running && startTime !== null) {
      currentElapsed += performance.now() - startTime;
    }

    var el = typeof document !== "undefined"
      ? document.getElementById("stopwatch-display")
      : null;

    if (el) {
      el.textContent = formatTime(currentElapsed);
    }
  }

  // ---------------------------------------------------------------------------
  // Wire up DOM buttons (browser only)
  // ---------------------------------------------------------------------------

  function initButtons() {
    var btnStart = document.getElementById("btn-start");
    var btnStop = document.getElementById("btn-stop");
    var btnReset = document.getElementById("btn-reset");

    if (btnStart) btnStart.addEventListener("click", start);
    if (btnStop) btnStop.addEventListener("click", stop);
    if (btnReset) btnReset.addEventListener("click", reset);
  }

  // ---------------------------------------------------------------------------
  // Export
  // ---------------------------------------------------------------------------

  if (typeof module !== "undefined" && module.exports) {
    // CommonJS / Jest environment
    module.exports = { start: start, stop: stop, reset: reset, formatTime: formatTime };
  } else {
    // Browser environment
    global.Stopwatch = { start: start, stop: stop, reset: reset };

    // Initialise button listeners once the DOM is ready
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", initButtons);
    } else {
      initButtons();
    }
  }
})(typeof window !== "undefined" ? window : global);
