// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'GitHub Trending Reporter',
  tagline: '每日 GitHub 热门项目追踪与 AI 分析',
  favicon: 'img/logo.svg',

  url: 'https://wayyoungboy.github.io',
  baseUrl: '/github-trending-reporter/',

  organizationName: 'wayyoungboy',
  projectName: 'github-trending-reporter',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  // 插件配置 - 复制 markdown 源文件到静态目录
  plugins: [
    async function copyMarkdownPlugin(context, options) {
      return {
        name: 'copy-markdown-plugin',
        async postBuild({ outDir }) {
          const fs = require('fs');
          const path = require('path');
          
          // 复制 reports 目录到 build 目录
          const copyDir = (src, dest) => {
            if (!fs.existsSync(dest)) {
              fs.mkdirSync(dest, { recursive: true });
            }
            const files = fs.readdirSync(src);
            for (const file of files) {
              const srcPath = path.join(src, file);
              const destPath = path.join(dest, file);
              const stat = fs.statSync(srcPath);
              if (stat.isDirectory()) {
                copyDir(srcPath, destPath);
              } else if (file.endsWith('.md')) {
                fs.copyFileSync(srcPath, destPath);
              }
            }
          };
          
          const reportsDir = path.join(context.siteDir, 'reports');
          const outReportsDir = path.join(outDir, 'reports');
          if (fs.existsSync(reportsDir)) {
            copyDir(reportsDir, outReportsDir);
          }
        },
      };
    },
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          path: 'reports',
          routeBasePath: 'reports',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: true,
        respectPrefersColorScheme: false,
      },
      image: 'img/social-card.jpg',
      navbar: {
        title: 'GitHub Trending Reporter',
        logo: {
          alt: 'Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'reportsSidebar',
            position: 'left',
            label: '每日报告',
          },
          {
            href: 'https://github.com/wayyoungboy/github-trending-reporter',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: '报告',
            items: [
              {
                label: '每日报告',
                to: '/reports/2026/01/2026-01-12',
              },
            ],
          },
          {
            title: '链接',
            items: [
              {
                label: 'GitHub Trending',
                href: 'https://github.com/trending',
              },
              {
                label: '源代码',
                href: 'https://github.com/wayyoungboy/github-trending-reporter',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} GitHub Trending Reporter. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
