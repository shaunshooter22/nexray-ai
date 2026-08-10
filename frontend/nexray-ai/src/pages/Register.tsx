// ============================================================
// NexRay AI - Register Page
// Allows new doctors to create an account.
// Requires full name, email, password and medical licence number.
// ============================================================

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

export default function Register() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    licence_number: "",
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.full_name || !form.email || !form.password || !form.licence_number) {
      toast.error("Please fill in all fields");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Registration failed");
      }
      toast.success("Account created! Please sign in.");
      navigate("/login");
    } catch (err: any) {
      toast.error(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
      <div className="flex flex-col gap-1.5">
        <label className="text-label text-text-primary" htmlFor="full_name">
          Full name
        </label>
        <input
          id="full_name"
          name="full_name"
          type="text"
          placeholder="Dr. John Mensah"
          value={form.full_name}
          onChange={handleChange}
          className="h-10 rounded-md border border-border px-3 text-body-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-label text-text-primary" htmlFor="email">
          Hospital email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          placeholder="you@hospital.gov.gh"
          value={form.email}
          onChange={handleChange}
          className="h-10 rounded-md border border-border px-3 text-body-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-label text-text-primary" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          placeholder="••••••••"
          value={form.password}
          onChange={handleChange}
          className="h-10 rounded-md border border-border px-3 text-body-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-label text-text-primary" htmlFor="licence_number">
          Medical licence number
        </label>
        <input
          id="licence_number"
          name="licence_number"
          type="text"
          placeholder="GH-MED-2026-001"
          value={form.licence_number}
          onChange={handleChange}
          className="h-10 rounded-md border border-border px-3 text-body-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        />
      </div>

      <Button type="submit" size="lg" className="w-full" disabled={loading}>
        {loading ? "Creating account..." : "Create account"}
      </Button>

      <p className="text-center text-body-sm text-text-secondary">
        Already have an account?{" "}
        <a href="/login" className="text-primary hover:underline font-medium">
          Sign in
        </a>
      </p>
    </form>
  );
}