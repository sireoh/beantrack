import React from "react";

export interface NavbarTitleProps {
  url: string;
  src: string;
  alt: string;
  title: string;
}

const NavbarTitle = ({ url, src, alt, title }: NavbarTitleProps) => {
  return (
    <>
      <a href={url} className="flex items-center gap-2">
        <img src={src} className="max-h-8" alt={alt} />
        <span className="text-lg font-semibold tracking-tighter text-white">
          {title}
        </span>
      </a>
    </>
  );
};

export default NavbarTitle;
