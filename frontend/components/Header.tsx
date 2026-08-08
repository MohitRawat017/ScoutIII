"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { getStoredTheme, toggleTheme, type Theme } from "@/lib/theme";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    // rAF keeps this out of the effect body per react-hooks/set-state-in-effect
    const themeRaf = window.requestAnimationFrame(() => setTheme(getStoredTheme()));
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.cancelAnimationFrame(themeRaf);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  return (
    <header className={`site-header${scrolled ? " is-scrolled" : ""}`}>
      <nav className="nav container" aria-label="Main">
        <a className="brand" href="#top">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
            <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.6" />
            <circle cx="12" cy="12" r="3.5" fill="currentColor" />
          </svg>
          <span>Scoutii</span>
        </a>

        <ul className="nav-links">
          <li><a href="#intents">How it works</a></li>
          <li><a href="#philosophy">The agent</a></li>
          <li><a href="#examples">Examples</a></li>
          <li><a href="#chat">Try it</a></li>
        </ul>

        <div className="nav-actions">
          <button
            type="button"
            className="theme-toggle"
            aria-label={theme === "evening" ? "Switch to morning theme" : "Switch to evening theme"}
            onClick={() => setTheme(toggleTheme())}
          >
            {theme === "evening" ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
          </button>
        </div>
      </nav>
    </header>
  );
}
