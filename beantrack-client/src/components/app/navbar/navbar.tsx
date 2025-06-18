import NavRightAuth from "./nav-right-auth";
import NavbarTitle from "./nav-title";

const Navbar = () => {
  return (
    <section className="bg-sky-800">
      <nav className="flex py-4 items-center justify-between">
        <NavbarTitle />
        <NavRightAuth />
      </nav>
    </section>
  );
};

export { Navbar };
