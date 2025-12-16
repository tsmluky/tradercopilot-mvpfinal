import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

interface TypewriterMarkdownProps {
    content: string;
    speed?: number;
    onComplete?: () => void;
}

export const TypewriterMarkdown: React.FC<TypewriterMarkdownProps> = ({
    content,
    speed = 10,
    onComplete
}) => {
    const [displayedContent, setDisplayedContent] = useState("");
    const indexRef = useRef(0);

    useEffect(() => {
        // Reset if content changes heavily
        setDisplayedContent("");
        indexRef.current = 0;
    }, [content]);

    useEffect(() => {
        const timer = setInterval(() => {
            if (indexRef.current < content.length) {
                setDisplayedContent((prev) => prev + content.charAt(indexRef.current));
                indexRef.current += 1;
            } else {
                clearInterval(timer);
                if (onComplete) onComplete();
            }
        }, speed);

        return () => clearInterval(timer);
    }, [content, speed, onComplete]);

    return (
        <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{displayedContent}</ReactMarkdown>
            {indexRef.current < content.length && (
                <span className="inline-block w-2 h-4 bg-indigo-500 animate-pulse ml-1 align-middle" />
            )}
        </div>
    );
};
