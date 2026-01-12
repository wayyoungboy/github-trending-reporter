import React, { useState, useCallback } from 'react';
import styles from './styles.module.css';

/**
 * 报告操作组件 - 提供复制和下载功能
 * 支持 Markdown 格式和渲染后的 HTML 格式
 */
export default function ReportActions() {
  const [copyStatus, setCopyStatus] = useState('');
  const [showDropdown, setShowDropdown] = useState({ copy: false, download: false });

  // 获取文章内容元素
  const getArticleElement = useCallback(() => {
    return document.querySelector('article.markdown');
  }, []);

  // 获取 Markdown 源文件路径
  const getMarkdownPath = useCallback(() => {
    // 从当前 URL 推断 markdown 文件路径
    const path = window.location.pathname;
    // 移除 baseUrl 和 trailing slash
    const cleanPath = path.replace('/github-trending-reporter', '').replace(/\/$/, '');
    return cleanPath + '.md';
  }, []);

  // 复制 Markdown 格式
  const copyAsMarkdown = useCallback(async () => {
    try {
      const mdPath = getMarkdownPath();
      // 尝试获取原始 markdown 文件
      const response = await fetch(`/github-trending-reporter${mdPath}`);
      if (response.ok) {
        const text = await response.text();
        await navigator.clipboard.writeText(text);
        setCopyStatus('✅ Markdown 已复制!');
      } else {
        // 如果无法获取源文件，从 DOM 转换
        const article = getArticleElement();
        if (article) {
          const markdown = htmlToMarkdown(article);
          await navigator.clipboard.writeText(markdown);
          setCopyStatus('✅ Markdown 已复制!');
        }
      }
    } catch (error) {
      console.error('Copy failed:', error);
      // 降级方案：复制纯文本
      const article = getArticleElement();
      if (article) {
        await navigator.clipboard.writeText(article.innerText);
        setCopyStatus('✅ 纯文本已复制!');
      }
    }
    setTimeout(() => setCopyStatus(''), 2000);
    setShowDropdown({ copy: false, download: false });
  }, [getArticleElement, getMarkdownPath]);

  // 复制渲染后的 HTML 格式（富文本）
  const copyAsRichText = useCallback(async () => {
    try {
      const article = getArticleElement();
      if (article) {
        // 创建一个包含样式的 HTML blob
        const htmlContent = article.innerHTML;
        const blob = new Blob([htmlContent], { type: 'text/html' });
        const textBlob = new Blob([article.innerText], { type: 'text/plain' });
        
        await navigator.clipboard.write([
          new ClipboardItem({
            'text/html': blob,
            'text/plain': textBlob,
          }),
        ]);
        setCopyStatus('✅ 富文本已复制!');
      }
    } catch (error) {
      console.error('Rich copy failed:', error);
      // 降级方案
      const article = getArticleElement();
      if (article) {
        await navigator.clipboard.writeText(article.innerText);
        setCopyStatus('✅ 纯文本已复制!');
      }
    }
    setTimeout(() => setCopyStatus(''), 2000);
    setShowDropdown({ copy: false, download: false });
  }, [getArticleElement]);

  // 下载 Markdown 文件
  const downloadAsMarkdown = useCallback(async () => {
    try {
      const mdPath = getMarkdownPath();
      const filename = mdPath.split('/').pop() || 'report.md';
      
      // 尝试获取原始文件
      const response = await fetch(`/github-trending-reporter${mdPath}`);
      let content;
      
      if (response.ok) {
        content = await response.text();
      } else {
        // 从 DOM 转换
        const article = getArticleElement();
        content = article ? htmlToMarkdown(article) : '';
      }
      
      downloadFile(content, filename, 'text/markdown');
    } catch (error) {
      console.error('Download failed:', error);
    }
    setShowDropdown({ copy: false, download: false });
  }, [getArticleElement, getMarkdownPath]);

  // 下载 HTML 文件
  const downloadAsHtml = useCallback(() => {
    try {
      const article = getArticleElement();
      if (article) {
        const title = document.querySelector('h1')?.innerText || 'GitHub Trending Report';
        const htmlContent = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    :root {
      --primary-color: #6366f1;
      --bg-color: #0f0f23;
      --text-color: #e4e4e7;
      --border-color: #27272a;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      background: var(--bg-color);
      color: var(--text-color);
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem;
      line-height: 1.7;
    }
    h1, h2, h3 { color: #fff; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }
    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; margin-top: 2rem; }
    h3 { font-size: 1.25rem; }
    a { color: var(--primary-color); text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { background: #1e1e3f; padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.9em; }
    pre { background: #1e1e3f; padding: 1rem; border-radius: 8px; overflow-x: auto; }
    blockquote { border-left: 4px solid var(--primary-color); margin: 1rem 0; padding-left: 1rem; color: #a1a1aa; }
    hr { border: none; border-top: 1px solid var(--border-color); margin: 2rem 0; }
    img { max-width: 100%; border-radius: 8px; }
    ul, ol { padding-left: 1.5rem; }
    li { margin: 0.5rem 0; }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    th, td { border: 1px solid var(--border-color); padding: 0.75rem; text-align: left; }
    th { background: #1e1e3f; }
  </style>
</head>
<body>
${article.innerHTML}
<footer style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border-color); color: #71717a; font-size: 0.875rem;">
  <p>Generated by GitHub Trending Reporter</p>
</footer>
</body>
</html>`;
        
        const filename = (title.match(/\d{4}-\d{2}-\d{2}/) || ['report'])[0] + '.html';
        downloadFile(htmlContent, filename, 'text/html');
      }
    } catch (error) {
      console.error('HTML download failed:', error);
    }
    setShowDropdown({ copy: false, download: false });
  }, [getArticleElement]);

  // 下载文件辅助函数
  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // 简单的 HTML to Markdown 转换
  const htmlToMarkdown = (element) => {
    let markdown = '';
    const walk = (node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        markdown += node.textContent;
        return;
      }
      if (node.nodeType !== Node.ELEMENT_NODE) return;

      const tag = node.tagName.toLowerCase();
      
      switch (tag) {
        case 'h1':
          markdown += '\n# ' + node.innerText + '\n\n';
          break;
        case 'h2':
          markdown += '\n## ' + node.innerText + '\n\n';
          break;
        case 'h3':
          markdown += '\n### ' + node.innerText + '\n\n';
          break;
        case 'h4':
          markdown += '\n#### ' + node.innerText + '\n\n';
          break;
        case 'p':
          markdown += node.innerText + '\n\n';
          break;
        case 'a':
          markdown += '[' + node.innerText + '](' + node.href + ')';
          break;
        case 'strong':
        case 'b':
          markdown += '**' + node.innerText + '**';
          break;
        case 'em':
        case 'i':
          markdown += '*' + node.innerText + '*';
          break;
        case 'code':
          if (node.parentElement?.tagName.toLowerCase() === 'pre') {
            markdown += '\n```\n' + node.innerText + '\n```\n\n';
          } else {
            markdown += '`' + node.innerText + '`';
          }
          break;
        case 'pre':
          if (!node.querySelector('code')) {
            markdown += '\n```\n' + node.innerText + '\n```\n\n';
          } else {
            node.childNodes.forEach(walk);
          }
          break;
        case 'ul':
          node.querySelectorAll(':scope > li').forEach((li) => {
            markdown += '- ' + li.innerText + '\n';
          });
          markdown += '\n';
          break;
        case 'ol':
          node.querySelectorAll(':scope > li').forEach((li, i) => {
            markdown += (i + 1) + '. ' + li.innerText + '\n';
          });
          markdown += '\n';
          break;
        case 'blockquote':
          markdown += '> ' + node.innerText.split('\n').join('\n> ') + '\n\n';
          break;
        case 'hr':
          markdown += '\n---\n\n';
          break;
        case 'img':
          markdown += '![' + (node.alt || '') + '](' + node.src + ')\n\n';
          break;
        case 'br':
          markdown += '\n';
          break;
        default:
          node.childNodes.forEach(walk);
      }
    };
    
    element.childNodes.forEach(walk);
    return markdown.trim();
  };

  // 切换下拉菜单
  const toggleDropdown = (type) => {
    setShowDropdown(prev => ({
      copy: type === 'copy' ? !prev.copy : false,
      download: type === 'download' ? !prev.download : false,
    }));
  };

  // 点击外部关闭下拉菜单
  React.useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest(`.${styles.actionGroup}`)) {
        setShowDropdown({ copy: false, download: false });
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <div className={styles.container}>
      {copyStatus && <div className={styles.toast}>{copyStatus}</div>}
      
      <div className={styles.actions}>
        {/* 复制按钮组 */}
        <div className={styles.actionGroup}>
          <button
            className={styles.actionButton}
            onClick={() => toggleDropdown('copy')}
            title="复制内容"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
            <span>复制</span>
            <svg className={styles.chevron} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          
          {showDropdown.copy && (
            <div className={styles.dropdown}>
              <button onClick={copyAsMarkdown} className={styles.dropdownItem}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <span>Markdown 格式</span>
                <span className={styles.hint}>.md 源码</span>
              </button>
              <button onClick={copyAsRichText} className={styles.dropdownItem}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.375 2.625a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4Z" />
                </svg>
                <span>富文本格式</span>
                <span className={styles.hint}>保留样式</span>
              </button>
            </div>
          )}
        </div>

        {/* 下载按钮组 */}
        <div className={styles.actionGroup}>
          <button
            className={styles.actionButton}
            onClick={() => toggleDropdown('download')}
            title="下载内容"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            <span>下载</span>
            <svg className={styles.chevron} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          
          {showDropdown.download && (
            <div className={styles.dropdown}>
              <button onClick={downloadAsMarkdown} className={styles.dropdownItem}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <span>下载 Markdown</span>
                <span className={styles.hint}>.md 文件</span>
              </button>
              <button onClick={downloadAsHtml} className={styles.dropdownItem}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="16 18 22 12 16 6" />
                  <polyline points="8 6 2 12 8 18" />
                </svg>
                <span>下载 HTML</span>
                <span className={styles.hint}>带样式网页</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
