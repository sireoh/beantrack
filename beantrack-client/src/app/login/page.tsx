import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex items-center justify-center h-[calc(80vh)] lg:h-[calc(90vh)]">
      <div className="w-full max-w-7xl shadow-lg rounded-lg overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2">
          {/* Sign-in Form */}
          <div className="flex items-center justify-center p-8 lg:border-r">
            <div className="w-full max-w-md space-y-6">
              <h5 className="text-2xl font-semibold">Sign in</h5>

              <form method="post" action="/signin" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">E-mail address</Label>
                  <Input
                    id="email"
                    name="username"
                    type="email"
                    placeholder="Your e-mail address"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Your password"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox id="remember" name="remember" />
                  <Label htmlFor="remember">Remember me</Label>
                </div>

                <input
                  type="hidden"
                  name="g-recaptcha-response"
                  value="[g-recaptcha-token]"
                />

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
                  <Button type="submit" className="w-full">
                    Sign in
                  </Button>
                  <Link
                    href="/signin/forgot_password"
                    className="text-sm text-blue-600 hover:underline self-center text-center">
                    Forgot your password?
                  </Link>
                </div>
              </form>
            </div>
          </div>

          {/* Signup Description */}
          <div className="hidden lg:flex items-center justify-center p-8">
            <div className="w-full max-w-md space-y-6">
              <h5 className="text-2xl font-semibold">Don't have an account?</h5>
              <p className="font-medium">
                Sign up for MyDramaList and gain access to a world of Asian
                dramas and movies. It's quick, easy, and completely free!
              </p>
              <p>
                By creating an account, you can enjoy the following features:
              </p>
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li>Create your own personalized drama list</li>
                <li>Join in discussions with other fans</li>
                <li>Contribute to the ever-growing database</li>
                <li>Rate and review dramas and movies</li>
                <li>Keep track of your favorite actors and actresses</li>
                <li>Discover new and exciting content</li>
                <li>Less advertisements</li>
                <li>And much more!</li>
              </ul>
              <p>
                Don't miss out — sign up now and start enjoying all the benefits
                of MyDramaList.
              </p>
              <Link href="/signup">
                <Button variant="outline" className="w-fit">
                  Sign up
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
