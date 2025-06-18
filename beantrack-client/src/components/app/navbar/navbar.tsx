import NavLoginButton from "./nav-login-btn";
import NavRightAuth from "./nav-right-auth";
import NavbarTitle from "./nav-title";

const Navbar = () => {
  return (
    <section className="bg-sky-800">
      <nav className="flex py-3 items-center justify-between">
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
