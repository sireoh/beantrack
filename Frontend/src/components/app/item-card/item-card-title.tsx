import useIsMobile, { ScreenSize } from "@/hooks/is-mobile";
import Link from "next/link";
import React from "react";

const ItemCardTitle = ({
  isTV,
  title,
  link,
  Year,
  premiered,
  ended,
}: {
  isTV: boolean;
  title: string;
  link: string;
  Year?: string;
  premiered?: string;
  ended?: string;
}) => {
  const isMobile = useIsMobile(ScreenSize.MOBILE);

  const MAX_LENGTH = isMobile === null ? 0 : isMobile ? 45 : Infinity;

  return (
    <Link href={link}>
      {isTV
        ? __handleTVShowTitle(title, premiered, ended)
        : __handleMovieTitle(title, MAX_LENGTH, Year)}
    </Link>
  );
};

function __handleTVShowTitle(
  name: string,
  premiered?: string,
  ended?: string
): string {
  const startYear = premiered?.split("-")[0] ?? "N/A";
  const endYear = ended?.split("-")[0] ?? "";

  if (startYear === endYear) return `${name} (${startYear})`;

  return `${name} (${startYear}${endYear ? `–${endYear}` : ""})`;
}

function __handleMovieTitle(
  title: string,
  maxCharacters: number,
  year?: string
): string {
  const yearPart = ` (${year})`;
  const maxTitleLength = maxCharacters - yearPart.length;

  if (title.length <= maxTitleLength) {
    return `${title}${yearPart}`;
  }

  const truncatedTitle = title.slice(0, maxTitleLength - 3).trimEnd(); // -3 for "..."
  return `${truncatedTitle} ...${yearPart}`;
}

export default ItemCardTitle;
