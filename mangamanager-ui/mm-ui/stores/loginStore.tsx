import { persistentMap } from "@nanostores/persistent";

const url = import.meta.env.SECRET_QAAPI;

interface LoginRep {
  token: string;
  tokenType: string;
}

async function postLogin(url: string, data: JSON): Promise<Response> {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(
      `Blast! Our letter was not received favorably: ${response.statusText}`
    );
  }
  console.log(response.json());
  return await response.json();
}
