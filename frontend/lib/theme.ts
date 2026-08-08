/**
 * Theme handling — "Morning Studio" (light, default) / "Evening Studio" (dark).
 * Persisted in localStorage, applied via `data-theme` on <html>.
 */

export const THEME_KEY = "scoutii-theme";
export type Theme = "light" | "evening";

/** Inline script injected in <head> — runs before first paint, no flash. */
export const themeInitScript = `(function(){try{var t=localStorage.getItem(${JSON.stringify(
  THEME_KEY
)});if(t==="evening"){document.documentElement.dataset.theme="evening";}}catch(e){}})();`;

export function getStoredTheme(): Theme {
  if (typeof window === "undefined") return "light";
  try {
    return window.localStorage.getItem(THEME_KEY) === "evening" ? "evening" : "light";
  } catch {
    return "light";
  }
}

export function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
}

export function toggleTheme(): Theme {
  const next: Theme = getStoredTheme() === "evening" ? "light" : "evening";
  try {
    window.localStorage.setItem(THEME_KEY, next);
  } catch {
    /* storage unavailable — theme still applies for this session */
  }
  applyTheme(next);
  return next;
}
