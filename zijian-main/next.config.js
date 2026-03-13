/** @type {import('next').NextConfig} */
const nextConfig = {
  // 跳过 ESLint 构建检查（缺少 @typescript-eslint 插件导致规则定义丢失）
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Next.js 15: 服务器外部包配置（从 experimental 移出）
  serverExternalPackages: ['@prisma/client', 'bcryptjs'],
  // 图片域名配置
  images: {
    domains: [],
  },
  // 环境变量（客户端可访问）
  env: {
    NEXT_PUBLIC_APP_NAME: '字见',
    NEXT_PUBLIC_APP_VERSION: '0.1.0',
  },
  // 安全响应头：允许被其他网站（如魔搭创空间）通过 Iframe 嵌入
  async headers() {
    return [
      {
        // 匹配所有路由
        source: '/(.*)',
        headers: [
          // 允许被嵌套。如果只想限制在魔搭，可以将 * 改为魔搭的域名
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors *;"
          },
          {
            key: 'X-Frame-Options',
            value: 'ALLOWALL' // 或者移除原有的 DENY/SAMEORIGIN 设置
          }
        ],
      },
    ];
  },
}

module.exports = nextConfig
