module.exports = {
  apps: [
    {
      name: 'yandex_lyceum_web_project',
      script: 'main.py',
      env: {
        NODE_ENV: 'development',
        NODE_APP_INSTANCE: '0'
      },
      env_production: {
        NODE_ENV: 'production',
        NODE_APP_INSTANCE: '0'
      }
    }
  ]
}
