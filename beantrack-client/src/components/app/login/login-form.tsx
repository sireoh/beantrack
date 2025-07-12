"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import LoginPassword from "@/components/app/login/login-password";
import { logToServer } from "@/utils/devlog-helper";
import { hydrateWatchlists } from "@/utils/hydrate-watchlists";
import { useStore } from "@/store";

const LoginForm = () => {
  const watchlists = useStore((state) => state.watchlists);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);

    const body = JSON.stringify({
      username: formData.get("username"),
      password: formData.get("password"),
    });

    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body,
      });

      if (res.ok) {
        window.location.href = "/";
      } else {
        alert("Login failed");
      }
    } catch (err) {
      console.error("Network or server error:", err);
    }
  };

  return (
    <form onSubmit={handleLogin} className="space-y-2">
      <div className="space-y-2">
        <Label htmlFor="username" className="font-bold">
          Username:
        </Label>
        <Input
          id="username"
          name="username"
          type="text"
          placeholder="username ..."
        />
      </div>

      <LoginPassword />

      <div className="flex justify-center mt-5">
        <Button
          type="submit"
          className="md:w-100 lg:w-25 font-black bg-sky-800 dark:bg-sky-600 cursor-pointer">
          Log on
        </Button>
      </div>
    </form>
  );
};

export default LoginForm;
