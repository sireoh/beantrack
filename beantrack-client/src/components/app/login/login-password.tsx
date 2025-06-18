"use client";

import { Label } from "@radix-ui/react-label";
import React, { useState } from "react";
import { Input } from "../../ui/input";
import { Eye, EyeOff } from "lucide-react";
import { Button } from "../../ui/button";

const LoginPassword = () => {
  const [show, setShow] = useState(false);
  return (
    <div className="space-y-2">
      <Label htmlFor="password" className="font-bold text-sm">
        Password:
      </Label>
      <div className="relative">
        <Input
          className="mt-1"
          id="password"
          name="password"
          type={show ? "text" : "password"}
          placeholder="password ..."
        />
        <Button
          type="button"
          variant="ghost"
          tabIndex={-1}
          onClick={() => setShow((prev) => !prev)}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-0 h-auto text-muted-foreground hover:bg-transparent">
          {show ? <EyeOff size={20} /> : <Eye size={20} />}
        </Button>
      </div>
    </div>
  );
};

export default LoginPassword;
