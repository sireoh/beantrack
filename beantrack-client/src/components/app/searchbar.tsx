"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { Form, FormField, FormItem, FormControl } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { useRouter } from "next/navigation";

const formSchema = z.object({
  q: z.string().min(1, { message: "Please enter a search term." }),
});

export function Searchbar() {
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
        <div className="flex items-center space-x-2">
          <FormField
            control={form.control}
            name="q"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Input
                    placeholder="Search..."
                    className="h-8 px-2 rounded border"
                    {...field}
                  />
                </FormControl>
              </FormItem>
            )}
          />
          <Button type="submit" className="px-3 py-2">
            <Search className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </Form>
  );
}

export function SearchbarMobile() {
  return (
    <Button type="submit" className="px-3 py-2">
      <Search className="h-4 w-4" />
    </Button>
  );
}
