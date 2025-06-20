"use client";

import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { LogOut } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const LogoutButton = () => {
  const router = useRouter();
  const handleLogout = async () => {
    try {
      const res = await fetch("/api/logout", {
        method: "POST",
        credentials: "include",
      });

      if (res.ok) {
        window.location.reload();
        router.push("/");
      } else {
        console.error("Logout failed:", await res.text());
      }
    } catch (err) {
      console.error("Logout error:", err);
    }
  };

  return (
    <DropdownMenuItem asChild onClick={handleLogout}>
      <Link href="#">
        <LogOut />
        Logout
      </Link>
    </DropdownMenuItem>
  );
};

export default LogoutButton;
