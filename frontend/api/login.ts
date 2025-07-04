import type { APIRoute } from "astro";

export const POST: APIRoute = async function POST({ request }) {
  const response = await fetch("http://127.0.0.1:8000/login", {
    method: "POST",
    body: request.formData(),
  });
  const token = await response.json();
  return token;
};
