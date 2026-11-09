
"use client";

import { useEffect, useState } from "react";
import GraphEditor from "./GraphEditor";
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
  const [selectedProject, setSelectedProject] = useState<number | null>(null);

  // Load saved projects from FastAPI
  async function loadProjects() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/projects`);

      if (!response.ok) {
        throw new Error("Unable to load projects");
      }

      const data: Project[] = await response.json();
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

      {/* Header */}
      <header className="border-b border-slate-200 bg-white px-6 py-5">
        <div className="mx-auto flex max-w-5xl items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 font-bold text-white">
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

      <div className="mx-auto max-w-5xl px-6 py-10">

        {/* Page Title */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold">Projects</h2>
          <p className="mt-2 text-slate-500">
            Manage your AI agent permission analysis projects.
          </p>
        </div>

        {/* Create Project */}
        <section className="mb-8 rounded-xl border border-slate-200 bg-white p-6">
          <h3 className="mb-4 font-semibold">
            Create New Project
          </h3>

          <form
            onSubmit={async (event) => {
              event.preventDefault();
              await createProject();
            }}
            className="flex flex-col gap-3 sm:flex-row"
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
              Create Project
            </button>
          </form>
        </section>

        {/* Error Message */}
        {error && (
          <p role="alert" className="mb-6 text-red-600">
            {error}
          </p>
        )}

        {/* Saved Projects */}
        <section>
          <h3 className="mb-4 text-lg font-semibold">
            Saved Projects
          </h3>

          {loading ? (
            <p className="text-slate-500">
              Loading projects...
            </p>
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
                    {new Date(
                      project.created_at
                    ).toLocaleDateString()}
                  </p>

                  {/* Open the project's graph */}
                  <button
                    onClick={() => setSelectedProject(project.id)}
                    className="mt-5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                  >
                    View Graph
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Selected Project Graph */}
        {selectedProject !== null && (
          <section className="mt-10 rounded-xl border border-slate-200 bg-white p-6">

            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-xl font-semibold">
                  Permission Graph
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  {projects.find(
                    (project) => project.id === selectedProject
                  )?.name || `Project #${selectedProject}`}
                </p>
              </div>

              <button
                onClick={() => setSelectedProject(null)}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-600 hover:bg-slate-100"
              >
                Close Graph
              </button>
            </div>

            <GraphEditor
              key={selectedProject}
              projectId={selectedProject}
            />
            {/* Graph Legend */}
            <div className="mt-5 flex flex-wrap gap-5 text-sm text-slate-600">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-blue-600" />
                Agent
              </div>

              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-slate-500" />
                Tool
              </div>

              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-emerald-600" />
                Public / Internal Resource
              </div>

              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-orange-700" />
                Confidential / Restricted Resource
              </div>
            </div>

          </section>
        )}

      </div>
    </main>
  );
}
