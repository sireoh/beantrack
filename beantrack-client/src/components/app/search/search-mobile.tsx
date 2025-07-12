"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormField, FormItem, FormControl } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { formSchema } from "./searchbar-desktop";
import { useStore } from "@/store";
import ChangeSearchTypeButton from "./change-search-type-button";

/**
 * Toggles the mobile searchbar visibility.
 */
export function SearchbarMobileToggleButton() {
  const navbar = useStore((state) => state.navbar);

  return (
    <Button
      variant="ghost"
      className="text-white mr-2 cursor-pointer"
      onClick={() => navbar.toggleExpand()}>
      <Search />
    </Button>
  );
}

/**
 * The searchbar exclusively used on mobile.
 */
export function MobileSearchbar() {
  const navbar = useStore((state) => state.navbar);
  const search = useStore((state) => state.search);

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
                      placeholder={
                        search.currentType !== "tv"
                          ? "Search Movies ..."
                          : "Search TV Shows ..."
                      }
                      onChange={(e) => {
                        field.onChange(e); // update react-hook-form
                        search.setValue(e.target.value); // update zustand
                      }}
                      value={field.value}
                      name={field.name}
                      ref={field.ref}
                      className="flex-1"
                    />
                  </FormControl>
                </FormItem>
              )}
            />
            <ChangeSearchTypeButton />
          </form>
        </Form>
      </div>
    )
  );
}
