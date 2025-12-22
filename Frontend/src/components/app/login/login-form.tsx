"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import LoginPassword from "@/components/app/login/login-password";
import { login } from "@/api/api";

const LoginForm = () => {
  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);

    const body = {
      username: formData.get("username") as string,
      password: formData.get("password") as string,
    };

    try {
      await login(body);
      window.location.href = "/";
    } catch (err) {
      console.error("Network or server error:", err);
      alert("Login failed");
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
