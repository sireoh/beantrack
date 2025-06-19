export async function logToServer(data: any) {
  try {
    await fetch("/api/devlog", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
  } catch (err) {
    console.error("Failed to send dev log:", err);
  }
}
