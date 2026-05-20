import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "AG-Visio",
    short_name: "AG-Visio",
    description: "AI-powered video conferencing with voice assistant, screen sharing, and remote desktop.",
    start_url: "/",
    display: "standalone",
    background_color: "#0a0a0a",
    theme_color: "#3b82f6",
    icons: [
      { src: "/favicon.ico", sizes: "48x48", type: "image/x-icon" },
      { src: "/icon.svg", sizes: "any", type: "image/svg+xml" },
    ],
  };
}
