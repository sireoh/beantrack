import { Button } from "@/components/ui/button";
import { LogIn } from "lucide-react";
import Link from "next/link";
import React from "react";

const NavbarLoginButton = () => {
  return (
    <Button asChild variant="outline" size="sm">
      <Link href="/login">
        <LogIn />
        Log In
      </Link>
    </Button>
  );
};

export default NavbarLoginButton;
