import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">📈 {siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link className="button button--secondary button--lg" to="/reports/2026/01/2026-01-12">
            🚀 查看最新报告
          </Link>
        </div>
      </div>
    </header>
  );
}

function Feature({emoji, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <div style={{fontSize: '3rem'}}>{emoji}</div>
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title="首页" description="每日 GitHub 热门项目追踪与 AI 分析报告">
      <HomepageHeader />
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              <Feature emoji="🔍" title="实时追踪" description="每日自动抓取 GitHub Trending 热门项目" />
              <Feature emoji="🤖" title="AI 分析" description="利用大语言模型对项目进行深度分析" />
              <Feature emoji="📊" title="数据持久化" description="历史数据完整保存，支持趋势回顾" />
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
