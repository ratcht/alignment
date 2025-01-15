'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css';

interface MarkdownDisplayProps {
  content: string;
}

const MarkdownDisplay = ({ content }: MarkdownDisplayProps) => {
  return (
    <div>
      <ReactMarkdown
        rehypePlugins={[rehypeRaw, rehypeSanitize, rehypeHighlight]}
        components={{
          h1: ({...props}) => <h1 className="text-3xl font-bold mb-4 mt-0" {...props} />,
          h2: ({...props}) => <h2 className="text-2xl font-bold mb-3 mt-0" {...props} />,
          h3: ({...props}) => <h3 className="text-xl font-bold mb-2 mt-0" {...props} />,
          p: ({...props}) => <p className="mb-4 mt-0" {...props} />,
          ul: ({...props}) => <ul className="list-disc ml-6 mb-4 mt-0" {...props} />,
          ol: ({...props}) => <ol className="list-decimal ml-6 mb-4 mt-0" {...props} />,
          li: ({...props}) => <li className="mb-1 mt-0" {...props} />,
          blockquote: ({...props}) => (
            <blockquote className="border-l-4 border-gray-300 pl-4 mb-4 mt-0 italic" {...props} />
          ),
          code: ({children, className, ...props}) => {
            const match = /language-(\w+)/.exec(className || '');
            return match ? (
              <pre className="block bg-gray-100 rounded p-4 mb-4 mt-0 overflow-auto">
                <code className={className} {...props}>
                  {children}
                </code>
              </pre>
            ) : (
              <code className="bg-gray-100 rounded px-1 py-0.5" {...props}>
                {children}
              </code>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>

    </div>
  );
};

export default MarkdownDisplay;