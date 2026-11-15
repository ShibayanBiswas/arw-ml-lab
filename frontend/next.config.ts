import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Phase 0: auth layout reads cookies(); full cacheComponents comes later.
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
