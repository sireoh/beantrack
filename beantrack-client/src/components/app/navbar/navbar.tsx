import NavLoginButton from "./nav-login-btn";
import NavRightAuth from "./nav-right-auth";
import NavbarTitle from "./nav-title";

const Navbar = () => {
  return (
    <section>
      <nav className="flex py-3 items-center justify-between fixed bg-sky-800 w-full shadow z-50 top-0 left-0">
        <NavbarTitle />
        {process.env.NEXT_PUBLIC_AUTHENTICATED == "true" ? (
          <NavRightAuth />
        ) : (
          <NavLoginButton />
        )}
      </nav>
    </section>
  );
};

export { Navbar };
