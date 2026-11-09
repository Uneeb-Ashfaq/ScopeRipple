
"use client";

import { useEffect, useState } from "react";

type Project = {
  id: number;
  name: string;
  created_at: string;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectName, setProjectName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // Load saved projects from FastAPI
  async function loadProjects() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/projects`);

      if (!response.ok) {
        throw new Error("Unable to load projects");
      }

      const data = await response.json();
      setProjects(data);
    } catch {
      setError("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  // Create a project and refresh the list
  async function createProject() {
    if (!projectName.trim()) {
      return;
    }

    try {
      setError("");

      const response = await fetch(`${API_URL}/projects`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: projectName.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to create project");
      }

      setProjectName("");
      await loadProjects();
    } catch {
      setError("Could not create project.");
    }
  }

  // Load projects when the page opens
  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-8 py-5">
        <div className="mx-auto flex max-w-5xl items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white font-bold">
            S
          </div>
          <div>
            <h1 className="text-xl font-bold">ScopeRipple</h1>
            <p className="text-sm text-slate-500">
              AI Agent Security Analyzer
            </p>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-8 py-10">
        <div className="mb-8">
          <h2 className="text-3xl font-bold">Projects</h2>
          <p className="mt-2 text-slate-500">
            Manage your AI agent permission analysis projects.
          </p>
        </div>

        <section className="mb-8 rounded-xl border border-slate-200 bg-white p-6">
          <h3 className="mb-4 font-semibold">Create New Project</h3>

          <form
            onSubmit={async (event) => {
              event.preventDefault();
              await createProject();
            }}
            className="flex gap-3"
          >
            <input
              type="text"
              value={projectName}
              maxLength={100}
              onChange={(event) => setProjectName(event.target.value)}
              placeholder="Project name"
              className="flex-1 rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
            />

            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-5 py-3 font-medium text-white hover:bg-blue-700"
            >
              Create
            </button>
          </form>
        </section>

        {error && (
          <p role="alert" className="mb-6 text-red-600">
            {error}
          </p>
        )}

        <section>
          <h3 className="mb-4 text-lg font-semibold">
            Saved Projects
          </h3>

          {loading ? (
            <p className="text-slate-500">Loading projects...</p>
          ) : projects.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
              No projects yet. Create your first project above.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="rounded-xl border border-slate-200 bg-white p-6"
                >
                  <h4 className="text-lg font-semibold">
                    {project.name}
                  </h4>

                  <p className="mt-2 text-sm text-slate-500">
                    Project #{project.id}
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    Created:{" "}
                    {new Date(project.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
