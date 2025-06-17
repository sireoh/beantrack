"use client";

import useIsMobile, { ScreenSize } from "@/hooks/is-mobile";
import React, { useState, useMemo } from "react";

// Fast HTML tag stripper
const stripHtml = (html: string): string => {
  return html.replace(/<[^>]*>/g, "").trim();
};

const ItemCardDescription = ({ description }: { description: string }) => {
  const isMobile = useIsMobile(ScreenSize.TABLET);
  const [expanded, setExpanded] = useState(false);

  // Strip tags only once
  const cleanDescription = useMemo(() => stripHtml(description), [description]);

  // Responsive max length
  const MAX_LENGTH =
    isMobile === null
      ? 144
      : isMobile
      ? 144 // mobile/tablet
      : 256; // desktop

  const isTruncated = cleanDescription.length > MAX_LENGTH;
  const visibleText =
    expanded || !isTruncated
      ? cleanDescription
      : cleanDescription.slice(0, MAX_LENGTH) + " ...";

  return (
    <p className="text-sm mt-2">
      {visibleText}
      {isTruncated && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-blue-500 hover:underline ml-1">
          {expanded ? "Show less" : "Read more"}
        </button>
      )}
    </p>
  );
};

export default ItemCardDescription;
