import React, { useEffect, useState, useRef } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

// 打字机效果 - 更流畅的实现
function TypeWriter({ texts, speed = 80 }) {
  const [displayText, setDisplayText] = useState('');
  const [textIndex, setTextIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentText = texts[textIndex];
    
    const timeout = setTimeout(() => {
      if (!isDeleting) {
        setDisplayText(currentText.substring(0, charIndex + 1));
        setCharIndex(charIndex + 1);
        
        if (charIndex === currentText.length) {
          setTimeout(() => setIsDeleting(true), 2500);
        }
      } else {
        setDisplayText(currentText.substring(0, charIndex - 1));
        setCharIndex(charIndex - 1);
        
        if (charIndex === 0) {
          setIsDeleting(false);
          setTextIndex((textIndex + 1) % texts.length);
        }
      }
    }, isDeleting ? speed / 2 : speed);

    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, textIndex, texts, speed]);

  return (
    <span className={styles.typewriter}>
      {displayText}
      <span className={styles.cursor}>|</span>
    </span>
  );
}

// 统计数字动画 - 带缓动效果
function AnimatedNumber({ end, duration = 2000, suffix = '' }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!isVisible) return;

    let startTime;
    const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);
    
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOutQuart(progress);
      
      setCount(Math.floor(easedProgress * end));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [end, duration, isVisible]);

  return <span ref={ref}>{count.toLocaleString()}{suffix}</span>;
}

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  
  return (
    <header className={styles.heroBanner}>
      <div className={styles.heroBackground}>
        <div className={styles.gridLines}></div>
        <div className={styles.glowOrb1}></div>
        <div className={styles.glowOrb2}></div>
        <div className={styles.glowOrb3}></div>
      </div>
      
      <div className={styles.heroContent}>
        <div className={styles.badge}>
          <span className={styles.badgeDot}></span>
          每日自动更新 · AI 驱动
        </div>
        
        <h1 className={styles.heroTitle}>
          追踪 GitHub 热门项目
          <br />
          <span className={styles.gradient}>
            <TypeWriter 
              texts={['AI 智能分析', '趋势洞察', '技术前沿', '开源动态', '深度解读']} 
              speed={70}
            />
          </span>
        </h1>
        
        <p className={styles.heroSubtitle}>
          自动爬取 GitHub Trending，通过大语言模型深度分析<br />
          每日为你呈现最具价值的开源项目报告
        </p>
        
        <div className={styles.heroButtons}>
          <Link className={styles.primaryButton} to="/reports/2026/01/2026-01-12">
            <span>📊 查看最新报告</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </Link>
          <a className={styles.secondaryButton} href="https://github.com/wayyoungboy/github-trending-reporter" target="_blank" rel="noopener noreferrer">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            <span>GitHub</span>
          </a>
        </div>

        {/* 代码预览 */}
        <div className={styles.codePreview}>
          <div className={styles.codeHeader}>
            <div className={styles.codeDots}>
              <span></span><span></span><span></span>
            </div>
            <span className={styles.codeTitle}>trending_reporter.py</span>
          </div>
          <pre className={styles.codeBlock}>
            <code>
              <span className={styles.keyword}>from</span> github_trending <span className={styles.keyword}>import</span> fetch_trending{'\n'}
              <span className={styles.keyword}>from</span> llm_analyzer <span className={styles.keyword}>import</span> LLMAnalyzer{'\n'}
              {'\n'}
              <span className={styles.comment}># 🔍 获取今日热门项目</span>{'\n'}
              repos = fetch_trending(language=<span className={styles.string}>"python"</span>){'\n'}
              {'\n'}
              <span className={styles.comment}># 🤖 AI 智能分析生成报告</span>{'\n'}
              analyzer = LLMAnalyzer(){'\n'}
              report = analyzer.generate_daily_report(repos){'\n'}
              {'\n'}
              <span className={styles.keyword}>print</span>(f<span className={styles.string}>"✨ 发现 </span>{'{'}len(repos){'}'}<span className={styles.string}> 个热门项目"</span>)
            </code>
          </pre>
        </div>
      </div>
    </header>
  );
}

function StatsSection() {
  return (
    <section className={styles.statsSection}>
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>
            <AnimatedNumber end={25} suffix="+" />
          </div>
          <div className={styles.statLabel}>每日追踪项目</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>
            <AnimatedNumber end={365} />
          </div>
          <div className={styles.statLabel}>天 × 24小时</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>
            <AnimatedNumber end={100} suffix="%" />
          </div>
          <div className={styles.statLabel}>自动化运行</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>∞</div>
          <div className={styles.statLabel}>历史数据保存</div>
        </div>
      </div>
    </section>
  );
}

function FeaturesSection() {
  const features = [
    {
      icon: '🔍',
      title: '智能数据采集',
      description: '每日自动爬取 GitHub Trending，获取最新热门项目数据，支持多语言过滤',
      gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    },
    {
      icon: '🤖',
      title: 'LLM 深度分析',
      description: '利用大语言模型对项目进行深度解读，提供技术洞察、趋势预测和学习建议',
      gradient: 'linear-gradient(135deg, #f472b6 0%, #fb7185 100%)',
    },
    {
      icon: '📊',
      title: '精美可视化',
      description: '生成结构化的 Markdown 报告，表格、图表、代码示例一应俱全',
      gradient: 'linear-gradient(135deg, #22d3ee 0%, #06b6d4 100%)',
    },
    {
      icon: '⚡',
      title: '全自动流水线',
      description: '基于 GitHub Actions 实现全流程自动化，每日定时触发，零人工干预',
      gradient: 'linear-gradient(135deg, #fb923c 0%, #f97316 100%)',
    },
    {
      icon: '💾',
      title: '历史数据归档',
      description: '所有报告永久保存，支持按日期浏览，构建你的技术知识库',
      gradient: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
    },
    {
      icon: '🌐',
      title: '在线预览',
      description: '基于 Docusaurus 构建的文档站点，随时随地在线阅读报告',
      gradient: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)',
    },
  ];

  return (
    <section className={styles.featuresSection}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionBadge}>✨ 核心功能</span>
        <h2 className={styles.sectionTitle}>为什么选择我们？</h2>
        <p className={styles.sectionSubtitle}>
          全方位的 GitHub 热门项目追踪与分析解决方案
        </p>
      </div>
      
      <div className={styles.featuresGrid}>
        {features.map((feature, idx) => (
          <div 
            key={idx} 
            className={styles.featureCard}
            style={{ '--card-accent': feature.gradient.split(',')[1]?.split(' ')[1] || '#6366f1' }}
          >
            <div className={styles.featureIcon} style={{ background: feature.gradient }}>
              {feature.icon}
            </div>
            <h3 className={styles.featureTitle}>{feature.title}</h3>
            <p className={styles.featureDescription}>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function WorkflowSection() {
  const steps = [
    { num: '01', title: '数据采集', desc: '爬取 GitHub Trending' },
    { num: '02', title: 'API 增强', desc: '获取详细项目信息' },
    { num: '03', title: 'AI 分析', desc: 'LLM 深度分析解读' },
    { num: '04', title: '报告生成', desc: 'Markdown 格式化' },
    { num: '05', title: '自动部署', desc: '站点实时更新' },
  ];

  return (
    <section className={styles.workflowSection}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionBadge}>⚙️ 工作流程</span>
        <h2 className={styles.sectionTitle}>自动化流水线</h2>
        <p className={styles.sectionSubtitle}>
          从数据采集到报告发布，全程自动化运行
        </p>
      </div>
      
      <div className={styles.workflowGrid}>
        {steps.map((step, idx) => (
          <div key={idx} className={styles.workflowStep}>
            <div className={styles.stepNumber}>{step.num}</div>
            <div className={styles.stepContent}>
              <h4>{step.title}</h4>
              <p>{step.desc}</p>
            </div>
            {idx < steps.length - 1 && <div className={styles.stepArrow}>→</div>}
          </div>
        ))}
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className={styles.ctaSection}>
      <div className={styles.ctaContent}>
        <h2>开始探索 GitHub 热门项目</h2>
        <p>每日更新 · AI 驱动 · 永不错过技术趋势</p>
        <div className={styles.ctaButtons}>
          <Link className={styles.ctaPrimary} to="/reports/2026/01/2026-01-12">
            🚀 立即查看报告
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <Layout title="首页" description="每日 GitHub 热门项目追踪与 AI 分析报告">
      <HomepageHeader />
      <main>
        <StatsSection />
        <FeaturesSection />
        <WorkflowSection />
        <CTASection />
      </main>
    </Layout>
  );
}
