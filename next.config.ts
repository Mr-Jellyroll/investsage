import { NextConfig } from 'next'

const config: NextConfig = {
  experimental: {
    serverActions: {
      allowedForwardedHosts: ["localhost"]
    }
  }
}

export default config