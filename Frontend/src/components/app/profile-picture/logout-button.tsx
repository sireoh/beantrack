"use client";

import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { LogOut } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const LogoutButton = () => {
  const router = useRouter();
  const handleLogout = async () => {
    window.location.reload();
    router.push("/");
  };

  return (
    <DropdownMenuItem asChild onClick={handleLogout}>
      <Link href="#" className="cursor-pointer">
        <LogOut />
        Logout
      </Link>
    </DropdownMenuItem>
  );
};

export default LogoutButton;
