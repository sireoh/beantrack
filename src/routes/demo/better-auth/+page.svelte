<script lang="ts">
  import { enhance } from "$app/forms";
  import type { PageServerData } from "./$types";
  import * as Card from "$lib/components/ui/card/index.js";
  import { Button } from "$lib/components/ui/button/index.js";

  let { data }: { data: PageServerData } = $props();
</script>

<div class="flex items-center justify-center p-8">
  <Card.Root class="w-full max-w-sm">
    <Card.Header>
      <Card.Title>Hi, {data.user.name}!</Card.Title>
      <Card.Description>Your user ID is {data.user.id}</Card.Description>
    </Card.Header>

    <Card.Footer>
      <form method="post" action="?/signOut" use:enhance class="w-full">
        <Button type="submit" variant="destructive" class="w-full">
          Sign out
        </Button>
      </form>
    </Card.Footer>
  </Card.Root>
</div>
