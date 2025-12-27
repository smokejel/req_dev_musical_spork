import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Disable strict mode for development to avoid double-rendering
  reactStrictMode: true,
};

export default nextConfig;
