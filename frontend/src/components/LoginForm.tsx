import { useState } from "react";
import type { FormEvent } from "react";

export default function Login() {
  const [responseMessage, setResponseMessage] = useState("");

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    console.log(data);
  }

  return (
    <body>
      <form onSubmit={submit}>
        <label>Username</label>
        <input type="text" id="username" name="username" />
        <label>Password</label>
        <input type="text" id="password" name="password" />
        <input type="submit" value="Submit" />
      </form>
    </body>
  );
}
