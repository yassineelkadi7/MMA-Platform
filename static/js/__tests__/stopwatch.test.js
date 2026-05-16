/**
 * Jest unit tests for stopwatch.js
 *
 * Requirements: 6.2, 6.3, 6.4, 6.5
 */

"use strict";

// Mock performance.now() for deterministic tests
let mockTime = 0;
global.performance = {
  now: () => mockTime,
};

// Mock setInterval / clearInterval
let intervalCallbacks = [];
let intervalIds = 0;
global.setInterval = (fn, ms) => {
  const id = ++intervalIds;
  intervalCallbacks.push({ id, fn });
  return id;
};
global.clearInterval = (id) => {
  intervalCallbacks = intervalCallbacks.filter((cb) => cb.id !== id);
};

// Mock fetch to detect any accidental network calls
global.fetch = jest.fn();

// Load the stopwatch module fresh for each test
let stopwatch;

beforeEach(() => {
  mockTime = 0;
  intervalCallbacks = [];
  intervalIds = 0;
  global.fetch.mockClear();

  // Re-require to reset module state
  jest.resetModules();
  stopwatch = require("../stopwatch");
});

// ---------------------------------------------------------------------------
// formatTime tests
// ---------------------------------------------------------------------------

describe("formatTime", () => {
  test("formats zero milliseconds as 00:00.0", () => {
    expect(stopwatch.formatTime(0)).toBe("00:00.0");
  });

  test("formats 1000 ms as 00:01.0", () => {
    expect(stopwatch.formatTime(1000)).toBe("00:01.0");
  });

  test("formats 60000 ms as 01:00.0", () => {
    expect(stopwatch.formatTime(60000)).toBe("01:00.0");
  });

  test("formats 90500 ms as 01:30.5", () => {
    expect(stopwatch.formatTime(90500)).toBe("01:30.5");
  });

  test("formats 5999900 ms (99:59.9) correctly", () => {
    expect(stopwatch.formatTime(5999900)).toBe("99:59.9");
  });

  test("clamps negative values to 00:00.0", () => {
    expect(stopwatch.formatTime(-500)).toBe("00:00.0");
  });

  test("formats 1500 ms as 00:01.5", () => {
    expect(stopwatch.formatTime(1500)).toBe("00:01.5");
  });
});

// ---------------------------------------------------------------------------
// start / stop / reset tests
// ---------------------------------------------------------------------------

describe("start", () => {
  test("start registers a setInterval callback", () => {
    stopwatch.start();
    expect(intervalCallbacks.length).toBe(1);
  });

  test("calling start twice does not register a second interval", () => {
    stopwatch.start();
    stopwatch.start();
    expect(intervalCallbacks.length).toBe(1);
  });
});

describe("stop", () => {
  test("stop clears the interval", () => {
    stopwatch.start();
    expect(intervalCallbacks.length).toBe(1);
    stopwatch.stop();
    expect(intervalCallbacks.length).toBe(0);
  });

  test("stop when not running is a no-op", () => {
    // Should not throw
    expect(() => stopwatch.stop()).not.toThrow();
    expect(intervalCallbacks.length).toBe(0);
  });

  test("elapsed time is retained after stop (can be resumed)", () => {
    // Advance time by 2000 ms, start, then stop
    mockTime = 0;
    stopwatch.start();
    mockTime = 2000;
    stopwatch.stop();

    // Start again and advance another 1000 ms
    stopwatch.start();
    mockTime = 3000;
    stopwatch.stop();

    // Total elapsed should be 2000 + 1000 = 3000 ms → 00:03.0
    expect(stopwatch.formatTime(3000)).toBe("00:03.0");
  });
});

describe("reset", () => {
  test("reset clears the interval", () => {
    stopwatch.start();
    stopwatch.reset();
    expect(intervalCallbacks.length).toBe(0);
  });

  test("reset while running clears the interval", () => {
    stopwatch.start();
    expect(intervalCallbacks.length).toBe(1);
    stopwatch.reset();
    expect(intervalCallbacks.length).toBe(0);
  });

  test("reset while paused is a no-op (no throw)", () => {
    stopwatch.start();
    stopwatch.stop();
    expect(() => stopwatch.reset()).not.toThrow();
  });
});

// ---------------------------------------------------------------------------
// fetch is never called
// ---------------------------------------------------------------------------

describe("no fetch calls", () => {
  test("fetch is never called during start", () => {
    stopwatch.start();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test("fetch is never called during stop", () => {
    stopwatch.start();
    stopwatch.stop();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test("fetch is never called during reset", () => {
    stopwatch.start();
    stopwatch.reset();
    expect(global.fetch).not.toHaveBeenCalled();
  });
});
