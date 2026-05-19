const { withSentryConfig } = require('@sentry/nextjs')
const nextConfig = { output: 'standalone' }
module.exports = withSentryConfig(nextConfig, { silent: true, hideSourceMaps: true })
