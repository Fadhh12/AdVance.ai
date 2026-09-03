"use client";

import { signIn } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { API_BASE_URL, readApiError } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    if (!response.ok) {
      setError(await readApiError(response));
      setIsSubmitting(false);
      return;
    }

    // Akun sudah dibuat — langsung masuk lewat NextAuth supaya session ke-set.
    const result = await signIn("credentials", { email, password, redirect: false });
    setIsSubmitting(false);

    if (result?.error) {
      // Registrasi berhasil tapi auto-login gagal (jarang) — arahkan ke login manual.
      router.push("/login");
      return;
    }
    router.push("/dashboard");
  }

  return (
    <main className="flex flex-1 items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-md bg-panel p-8">
        <h1 className="font-display text-2xl text-ink">Buat akun adVance.AI</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Foto produk pertamamu tinggal beberapa langkah lagi jadi video.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
          <TextField
            id="name"
            label="Nama"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <TextField
            id="email"
            label="Email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            id="password"
            label="Password"
            type="password"
            minLength={8}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && (
            <p className="rounded-md border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
              {error}
            </p>
          )}

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Membuat akun…" : "Daftar"}
          </Button>
        </form>

        <p className="mt-6 text-sm text-ink-muted">
          Sudah punya akun?{" "}
          <Link href="/login" className="text-rec hover:underline">
            Masuk
          </Link>
        </p>
      </div>
    </main>
  );
}
