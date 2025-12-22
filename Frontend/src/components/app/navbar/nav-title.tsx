import { Bean } from "lucide-react";
import Link from "next/link";

const NavbarTitle = () => {
  return (
    <Link href="/" className="flex items-center gap-2 ml-4">
      <Bean className="text-white" />
      <span className="text-lg font-semibold text-white">BeanTrack</span>
    </Link>
  );
};

export default NavbarTitle;
