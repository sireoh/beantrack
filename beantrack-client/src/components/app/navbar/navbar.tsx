"use client";

import { useAuth } from "@/hooks/use-auth";
import NavLoginButton from "./nav-login-btn";
import NavRightAuth from "./nav-right-auth";
import NavbarTitle from "./nav-title";

const Navbar = () => {
  const { loading, user } = useAuth();

  return (
    <section>
      <nav className="flex py-3 items-center justify-between fixed bg-sky-800 w-full shadow z-50 top-0 left-0">
        <NavbarTitle />
        {!loading && user ? <NavRightAuth /> : <NavLoginButton />}
      </nav>
    </section>
  );
};

export { Navbar };
