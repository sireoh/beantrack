import { Power } from "lucide-react";
import LoginDescription from "@/components/app/login/login-description";
import LoginForm from "@/components/app/login/login-form";

export default function Home() {
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
                  Continue
                </span>
              </h1>

              <LoginForm />
            </div>
          </div>

          <LoginDescription />
        </div>
      </div>
    </div>
  );
}
