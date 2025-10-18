'use client';

import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * Renders markdown content with GitHub Flavored Markdown support
 * Includes syntax highlighting, tables, task lists, and more
 */
const MarkdownRenderer: React.FC<MarkdownRendererProps> = memo(({ content, className = '' }) => {
  return (
    <div className={`prose prose-sm max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Custom code block rendering with syntax highlighting
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';

            return !inline && language ? (
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={language}
                PreTag="div"
                className="rounded-lg !mt-2 !mb-4"
                customStyle={{
                  margin: 0,
                  borderRadius: '0.5rem',
                  fontSize: '0.875rem',
                }}
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code
                className="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded text-xs font-mono"
                {...props}
              >
                {children}
              </code>
            );
          },

          // Enhanced table styling
          table({ children, ...props }: any) {
            return (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full divide-y divide-gray-200 border border-gray-200" {...props}>
                  {children}
                </table>
              </div>
            );
          },

          thead({ children, ...props }: any) {
            return (
              <thead className="bg-gray-50" {...props}>
                {children}
              </thead>
            );
          },

          th({ children, ...props }: any) {
            return (
              <th
                className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200"
                {...props}
              >
                {children}
              </th>
            );
          },

          td({ children, ...props }: any) {
            return (
              <td className="px-4 py-2 text-sm text-gray-900 border-b border-gray-200" {...props}>
                {children}
              </td>
            );
          },

          // Enhanced blockquote styling
          blockquote({ children, ...props }: any) {
            return (
              <blockquote
                className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50 italic text-gray-700"
                {...props}
              >
                {children}
              </blockquote>
            );
          },

          // Task list styling
          input({ type, checked, ...props }: any) {
            if (type === 'checkbox') {
              return (
                <input
                  type="checkbox"
                  checked={checked}
                  disabled
                  className="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  {...props}
                />
              );
            }
            return <input type={type} {...props} />;
          },

          // Heading styles
          h1({ children, ...props }: any) {
            return (
              <h1 className="text-2xl font-bold mt-6 mb-4 text-gray-900 border-b pb-2" {...props}>
                {children}
              </h1>
            );
          },

          h2({ children, ...props }: any) {
            return (
              <h2 className="text-xl font-bold mt-5 mb-3 text-gray-900" {...props}>
                {children}
              </h2>
            );
          },

          h3({ children, ...props }: any) {
            return (
              <h3 className="text-lg font-semibold mt-4 mb-2 text-gray-900" {...props}>
                {children}
              </h3>
            );
          },

          h4({ children, ...props }: any) {
            return (
              <h4 className="text-base font-semibold mt-3 mb-2 text-gray-900" {...props}>
                {children}
              </h4>
            );
          },

          h5({ children, ...props }: any) {
            return (
              <h5 className="text-sm font-semibold mt-3 mb-1 text-gray-900" {...props}>
                {children}
              </h5>
            );
          },

          h6({ children, ...props }: any) {
            return (
              <h6 className="text-xs font-semibold mt-2 mb-1 text-gray-900" {...props}>
                {children}
              </h6>
            );
          },

          // Enhanced link styling
          a({ children, href, ...props }: any) {
            return (
              <a
                href={href}
                className="text-blue-600 hover:text-blue-800 underline hover:no-underline transition-colors"
                target="_blank"
                rel="noopener noreferrer"
                {...props}
              >
                {children}
              </a>
            );
          },

          // List styling
          ul({ children, ...props }: any) {
            return (
              <ul className="list-disc list-inside space-y-1 my-3" {...props}>
                {children}
              </ul>
            );
          },

          ol({ children, ...props }: any) {
            return (
              <ol className="list-decimal list-inside space-y-1 my-3" {...props}>
                {children}
              </ol>
            );
          },

          // Horizontal rule
          hr({ ...props }: any) {
            return <hr className="my-6 border-gray-300" {...props} />;
          },

          // Paragraph spacing
          p({ children, ...props }: any) {
            return (
              <p className="my-3 text-gray-700 leading-relaxed" {...props}>
                {children}
              </p>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
});

MarkdownRenderer.displayName = 'MarkdownRenderer';

export default MarkdownRenderer;
