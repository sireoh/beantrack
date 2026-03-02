<script lang="ts">
  import { enhance } from "$app/forms";
  import type { ActionData } from "./$types";
  import * as Field from "$lib/components/ui/field/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Button } from "$lib/components/ui/button/index.js";

  let { form }: { form: ActionData } = $props();
</script>

<div class="mx-auto w-full max-w-md space-y-6 py-8">
  <div class="space-y-2 text-center">
    <h1 class="text-3xl font-bold">Login</h1>
    <p class="text-muted-foreground text-sm">
      Enter your credentials to access your account
    </p>
  </div>

  <form method="post" action="?/signInEmail" use:enhance>
    <Field.Group>
      <Field.Field>
        <Field.Label for="email">Email</Field.Label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="name@example.com"
          required
        />
      </Field.Field>

      <Field.Field>
        <Field.Label for="password">Password</Field.Label>
        <Input id="password" name="password" type="password" required />
      </Field.Field>

      <Field.Field>
        <Field.Label for="name">Name (for registration)</Field.Label>
        <Input id="name" name="name" placeholder="Jane Doe" />
        <Field.Description
          >Only required if you are creating a new account.</Field.Description
        >
      </Field.Field>

      {#if form?.message}
        <p class="text-destructive text-sm font-medium">{form.message}</p>
      {/if}

      <div class="flex flex-col gap-3 pt-4">
        <Button type="submit" class="w-full">Login</Button>
        <Button variant="outline" formaction="?/signUpEmail" class="w-full">
          Register
        </Button>
      </div>
    </Field.Group>
  </form>
</div>
