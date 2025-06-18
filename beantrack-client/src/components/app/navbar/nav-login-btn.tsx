import { Button } from "@/components/ui/button";
import { LogIn } from "lucide-react";
import Link from "next/link";
import React from "react";

const NavLoginButton = () => {
  return (
    <Button asChild variant="outline" size="sm" className="mr-3">
      <Link href="/login">
        <LogIn />
        Log In
      </Link>
    </Button>
  );
};

export default NavLoginButton;
