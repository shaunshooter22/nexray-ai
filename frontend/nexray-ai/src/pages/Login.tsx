// ============================================================
// NexRay AI - Login Page
// Connects to the real backend auth route.
// Stores JWT token on successful login.
// ============================================================

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { login } from "@/lib/api";
import toast from "react-hot-toast";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Please enter your email and password");
      return;
    }
    setLoading(true);
    try {
      await login(email, password);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err) {
      toast.error("Incorrect email or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
      <div className="flex flex-col gap-1.5">
        <label className="text-label text-text-primary" htmlFor="email">
          Hospital email
        </label>
        <input
          id="email"
          type="email"
          placeholder="you@hospital.gov.gh"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="h-10 rounded-md border border-border px-3 text-body-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-label text-text-primary" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="h-10 rounded-md border border-border px-3 text-body-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        />
      </div>

      <div className="flex items-center justify-between text-body-sm">
        <label className="flex items-center gap-2 text-text-secondary">
          <input type="checkbox" className="rounded border-border" />
          Remember me
        </label>
        <a href="#" className="text-primary hover:underline">
          Forgot password?
        </a>
      </div>

      <Button type="submit" size="lg" className="w-full" disabled={loading}>
        {loading ? "Signing in..." : "Sign in"}
      </Button>

      <p className="text-center text-body-sm text-text-secondary">
        Don't have an account?{" "}
        <a href="/register" className="text-primary hover:underline font-medium">
          Register
        </a>
      </p>
    </form>
  );
}