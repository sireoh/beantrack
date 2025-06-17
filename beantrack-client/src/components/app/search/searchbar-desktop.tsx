"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Form, FormField, FormItem, FormControl } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import ChangeSearchTypeButton from "./change-search-type-button";

export const formSchema = z.object({
  q: z.string().min(1, { message: "Please enter a search term." }),
});

export function SearchbarDesktop() {
  const router = useRouter();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      q: "",
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    const query = encodeURIComponent(values.q);
    router.push(`/search?q=${query}`);
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        role="search"
        className="hidden md:flex items-center ml-auto">
        <div className="flex items-stretch">
          {" "}
          {/* removed space-x-2 */}
          <FormField
            control={form.control}
            name="q"
            render={({ field }) => (
              <FormItem className="h-full">
                <FormControl>
                  <Input
                    placeholder="Search ..."
                    className="h-full px-2 rounded-none border-l border-y placeholder:text-white selection:bg-sky-600 selection:text-white text-white border-gray-400"
                    {...field}
                  />
                </FormControl>
              </FormItem>
            )}
          />
          <ChangeSearchTypeButton />
        </div>
      </form>
    </Form>
  );
}
