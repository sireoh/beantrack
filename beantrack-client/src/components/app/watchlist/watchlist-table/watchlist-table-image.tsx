import Link from "next/link";
import Image from "next/image";
import React from "react";

const WatchlistTableImage = () => {
  return (
    <div className="flex justify-center items-center">
      <Link href="/anime/56038/Lazarus" className="link sort">
        <Image
          src="https://cdn.myanimelist.net/r/192x272/images/anime/1098/150300.jpg?s=419e7b1639949c581db4de0e03cf3669"
          alt="Lazarus"
          width={48}
          height={68}
          className="hover-info image"
        />
      </Link>
    </div>
  );
};

export default WatchlistTableImage;
