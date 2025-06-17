"use client";

import useIsMobile, { ScreenSize } from "@/hooks/is-mobile";
import React, { useState } from "react";

const ItemCardDescription = ({ description }: { description: string }) => {
  const isMobile = useIsMobile(ScreenSize.TABLET);
  const [expanded, setExpanded] = useState(false);

  // If null (still loading), default to tablet size just in case
  const MAX_LENGTH =
    isMobile === null
      ? 144
      : isMobile
      ? 144 // tablet or smaller
      : 256; // desktop

  const isTruncated = description.length > MAX_LENGTH;
  const visibleText =
    expanded || !isTruncated
      ? description
      : description.slice(0, MAX_LENGTH) + " ...";

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
