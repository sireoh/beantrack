import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Power } from "lucide-react";
import LoginPassword from "@/components/app/login/login-password";
import LoginDescription from "@/components/app/login/login-description";

export default function Home() {
  const _l = ["Log on", "Continue"];

  return (
    <div className="flex items-center justify-center h-[calc(48vh)] lg:h-[calc(90vh)]">
      <div className="shadow-lg rounded-xs">
        <div className="grid grid-cols-1 lg:grid-cols-2 md:w-[calc(80vw)]">
          {/* Sign-in Form */}
          <div className="flex items-center justify-center p-8 lg:border-r">
            <div className="w-full space-y-6">
              <h1 className="flex justify-center items-center">
                <span className="flex row gap-2 text-4xl font-black lg:text-5xl mr-12">
                  <Power
                    size={32}
                    className="mt-1 lg:mt-3 text-sky-800 dark:text-sky-600"
                    strokeWidth={4}
                  />
                  {_l[0]}
                </span>
              </h1>

              <form method="post" action="/api/login" className="space-y-2">
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
                    className="md:w-100 lg:w-25 font-black bg-sky-800 dark:bg-sky-600">
                    {_l[1]}
                  </Button>
                </div>
              </form>
            </div>
          </div>

          <LoginDescription />
        </div>
      </div>
    </div>
  );
}
