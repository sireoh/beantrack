import Image from "next/image";
import { useState } from "react";

export default function SafeImage({ src, alt }: { src: string; alt: string }) {
  const [imgSrc, setImgSrc] = useState(src);

  return (
    <Image
      src={imgSrc}
      alt={alt}
      width={90}
      height={128}
      onError={() => setImgSrc("/images/item-card-no-image.png")}
    />
  );
}
