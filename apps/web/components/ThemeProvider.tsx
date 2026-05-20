"use client";

import { useEffect } from "react";
import { useSettings } from "@/lib/settings";

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { settings } = useSettings();

  useEffect(() => {
    const html = document.documentElement;
    const theme = settings.theme || "dark";

    if (theme === "system") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      html.className = prefersDark ? "dark" : "";
    } else {
      html.className = theme === "dark" ? "dark" : "";
    }
  }, [settings.theme]);

  return <>{children}</>;
}
