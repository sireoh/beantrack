import { useEffect, useState } from "react";

export enum ScreenSize {
  MOBILE = 768, // < 768px → mobile
  TABLET = 1024, // < 1024px → tablet
  DESKTOP = Infinity, // ≥ 1024px → desktop
}

const useIsMobile = (breakpoint: number) => {
  const [isMobile, setIsMobile] = useState<boolean | null>(null);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < breakpoint);
    };

    handleResize(); // initial check on mount

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [breakpoint]);

  return isMobile;
};

export default useIsMobile;
