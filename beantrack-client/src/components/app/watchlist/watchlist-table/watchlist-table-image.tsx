import Link from "next/link";
import Image from "next/image";
import React, { useState } from "react";
import { MockDataInsideProps } from "./watchlist-table-body";

const WatchlistTableImage = ({
  image,
  title,
}: Pick<MockDataInsideProps, "image" | "title">) => {
  const _url = `https://static.tvmaze.com/uploads/images/original_untouched${image}.jpg`;

  return (
    <div className="flex justify-center items-center">
      <Link href="/anime/56038/Lazarus" className="link sort">
        <Image
          src={_url}
          alt={title}
          width={60}
          height={68}
          className="hover-info image"
        />
      </Link>
    </div>
  );
};

export default WatchlistTableImage;
