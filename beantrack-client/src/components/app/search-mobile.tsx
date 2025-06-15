"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormField, FormItem, FormControl } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { formSchema } from "./searchbar";
import { useStore } from "@/store";

export function SearchbarMobile() {
  const navbar = useStore((state) => state.navbar);

  return (
    <Button variant="ghost" onClick={() => navbar.toggleExpand()}>
      <Search />
    </Button>
  );
}

export function SearchbarMobileDropdown() {
  const navbar = useStore((state) => state.navbar);

  const router = useRouter();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      q: "",
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    const query = encodeURIComponent(values.q.trim());
    if (query) {
      router.push(`/search?q=${query}`);
    }
  }

  return (
    navbar.isExpanded && (
      <div className="p-4 bg-white dark:bg-gray-800">
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            role="search"
            className="flex gap-2">
            <FormField
              control={form.control}
              name="q"
              render={({ field }) => (
                <FormItem className="flex-1">
                  <FormControl>
                    <Input
                      placeholder="Search ..."
                      className="flex-1"
                      {...field}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <Button
              type="submit"
              variant="outline"
              className="flex-none text-black dark:text-white">
              <Search size={16} />
            </Button>
          </form>
        </Form>
      </div>
    )
  );
}
