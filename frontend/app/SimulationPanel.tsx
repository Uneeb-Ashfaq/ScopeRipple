
"use client";

import { useEffect, useState } from "react";

type GraphNode = {
  id: string;
  type: "agent" | "tool" | "resource";
  sensitivity: string;
};

type Permission = {
  source: string;
  target: string;
  action: "read" | "write" | "execute";
};

type Change = Permission & {
  operation: "add" | "remove";
};

type Access = {
  resource: string;
  action: string;
  sensitivity: string;
  path: string[];
};

type Finding = Access & {
  severity: string;
  reason: string;
};

type SimulationResult = {
  id: number;
  simulation: {
    new_access: Access[];
    lost_access: Access[];
  };
  findings: Finding[];
};

type Props = {
  projectId: number;
  refreshKey: number;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000/api/v1";

export default function SimulationPanel({
  projectId,
  refreshKey,
}: Props) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);

  const [agentId, setAgentId] = useState("");
  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  const [action, setAction] = useState<Permission["action"]>("read");
  const [operation, setOperation] = useState<Change["operation"]>("add");

  const [changes, setChanges] = useState<Change[]>([]);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  // Load the project's existing nodes and permissions
  useEffect(() => {
    let cancelled = false;

    async function loadGraph() {
      setNodes([]);
      setPermissions([]);
      setChanges([]);
      setResult(null);
      setError("");
      setAgentId("");
      setSource("");
      setTarget("");

      try {
        const response = await fetch(
          `${API_URL}/projects/${projectId}/graph`
        );

        if (!response.ok) {
          throw new Error("Unable to load project graph.");
        }

        const data = await response.json();

        if (!cancelled) {
          setNodes(data.nodes);
          setPermissions(data.permissions);
        }
      } catch {
        if (!cancelled) {
          setError("Could not load graph data.");
        }
      }
    }

    loadGraph();

    return () => {
      cancelled = true;
    };
  }, [projectId, refreshKey]);

  // Check whether an exact permission exists
  function permissionExists(
    list: Permission[],
    permission: Permission
  ) {
    return list.some(
      (item) =>
        item.source === permission.source &&
        item.target === permission.target &&
        item.action === permission.action
    );
  }

  // Queue a proposed change without modifying the database
  function addChange() {
    setError("");
    setResult(null);

    if (!source || !target) {
      setError("Select a source and target.");
      return;
    }

    if (source === target) {
      setError("Choose two different nodes.");
      return;
    }

    const permission = { source, target, action };

    // Calculate permissions after previously queued changes
    const current = [...permissions];

    for (const change of changes) {
      const item = {
        source: change.source,
        target: change.target,
        action: change.action,
      };

      if (change.operation === "add") {
        current.push(item);
      } else {
        const index = current.findIndex(
          (existing) =>
            existing.source === item.source &&
            existing.target === item.target &&
            existing.action === item.action
        );

        if (index !== -1) {
          current.splice(index, 1);
        }
      }
    }

    const exists = permissionExists(current, permission);

    if (operation === "add" && exists) {
      setError("This permission already exists.");
      return;
    }

    if (operation === "remove" && !exists) {
      setError("This permission does not exist.");
      return;
    }

    setChanges([...changes, { ...permission, operation }]);
    setSource("");
    setTarget("");
  }

  // Remove a queued change before running the simulation
  function removeChange(index: number) {
    setChanges(changes.filter((_, i) => i !== index));
    setResult(null);
    setError("");
  }

  // Run the queued changes using FastAPI
  async function runSimulation() {
    if (!agentId || changes.length === 0) {
      setError("Select an agent and add at least one change.");
      return;
    }

    setRunning(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/projects/${projectId}/simulations`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            agent_id: agentId,
            changes: changes,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Simulation failed."
        );
      }

      const data: SimulationResult = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Simulation failed."
      );
    } finally {
      setRunning(false);
    }
  }

  const agents = nodes.filter((node) => node.type === "agent");
  const sources = nodes.filter(
    (node) => node.type === "agent" || node.type === "tool"
  );

  return (
    <section className="space-y-6 rounded-xl border border-slate-200 bg-white p-6">
      <div>
        <h3 className="text-xl font-semibold">
          Security Simulation
        </h3>
        <p className="mt-1 text-sm text-slate-500">
          Test proposed permission changes without modifying
          the saved graph.
        </p>
      </div>

      {/* Select the agent being analyzed */}
      <div>
        <label className="mb-2 block text-sm font-medium">
          Agent to Analyze
        </label>
        <select
          value={agentId}
          onChange={(event) => {
            setAgentId(event.target.value);
            setResult(null);
          }}
          className="w-full rounded-lg border border-slate-300 p-3"
        >
          <option value="">Select agent</option>
          {agents.map((node) => (
            <option key={node.id} value={node.id}>
              {node.id}
            </option>
          ))}
        </select>
      </div>

      {/* Configure a permission change */}
      <div className="rounded-xl bg-slate-50 p-5">
        <h4 className="mb-4 font-semibold">
          Propose Permission Change
        </h4>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm">
              Source
            </label>
            <select
              value={source}
              onChange={(event) => setSource(event.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white p-3"
            >
              <option value="">Select source</option>
              {sources.map((node) => (
                <option key={node.id} value={node.id}>
                  {node.id}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm">
              Target
            </label>
            <select
              value={target}
              onChange={(event) => setTarget(event.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white p-3"
            >
              <option value="">Select target</option>
              {nodes
                .filter((node) => node.type !== "agent")
                .map((node) => (
                  <option key={node.id} value={node.id}>
                    {node.id}
                  </option>
                ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm">
              Action
            </label>
            <select
              value={action}
              onChange={(event) =>
                setAction(
                  event.target.value as Permission["action"]
                )
              }
              className="w-full rounded-lg border border-slate-300 bg-white p-3"
            >
              <option value="read">Read</option>
              <option value="write">Write</option>
              <option value="execute">Execute</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm">
              Operation
            </label>
            <select
              value={operation}
              onChange={(event) =>
                setOperation(
                  event.target.value as Change["operation"]
                )
              }
              className="w-full rounded-lg border border-slate-300 bg-white p-3"
            >
              <option value="add">Add Permission</option>
              <option value="remove">Remove Permission</option>
            </select>
          </div>
        </div>

        <button
          type="button"
          onClick={addChange}
          className="mt-4 rounded-lg border border-blue-600 px-4 py-2 font-medium text-blue-600 hover:bg-blue-50"
        >
          Add to Simulation
        </button>
      </div>

      {/* Show queued changes */}
      <div>
        <h4 className="mb-3 font-semibold">
          Proposed Changes ({changes.length})
        </h4>

        {changes.length === 0 ? (
          <p className="text-sm text-slate-500">
            No changes added yet.
          </p>
        ) : (
          <div className="space-y-2">
            {changes.map((change, index) => (
              <div
                key={index}
                className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 p-3"
              >
                <div className="text-sm">
                  <span className="font-semibold">
                    {change.operation.toUpperCase()}
                  </span>{" "}
                  {change.source} → {change.target} ({change.action})
                </div>

                <button
                  type="button"
                  onClick={() => removeChange(index)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={runSimulation}
        disabled={running || !agentId || changes.length === 0}
        className="w-full rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {running ? "Running Simulation..." : "Run Simulation"}
      </button>

      {/* Display the results returned by the backend */}
      {result && (
        <div className="space-y-5 border-t border-slate-200 pt-6">
          <div>
            <h4 className="text-xl font-semibold">
              Simulation Results
            </h4>
            <p className="text-sm text-slate-500">
              Saved simulation #{result.id}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              {
                label: "New Access",
                value: result.simulation.new_access.length,
              },
              {
                label: "Lost Access",
                value: result.simulation.lost_access.length,
              },
              {
                label: "Risk Findings",
                value: result.findings.length,
              },
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-lg bg-slate-50 p-4"
              >
                <p className="text-2xl font-bold">
                  {item.value}
                </p>
                <p className="text-sm text-slate-500">
                  {item.label}
                </p>
              </div>
            ))}
          </div>

          <div>
            <h5 className="mb-3 font-semibold">
              Security Findings
            </h5>

            {result.findings.length === 0 ? (
              <p className="text-sm text-slate-500">
                No new access risks detected by the current rules.
              </p>
            ) : (
              <div className="space-y-3">
                {result.findings.map((finding, index) => (
                  <div
                    key={index}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <span className="font-semibold">
                        {finding.resource}
                      </span>

                      <span className="rounded-md bg-orange-100 px-2 py-1 text-xs font-bold uppercase text-orange-800">
                        {finding.severity}
                      </span>
                    </div>

                    <p className="text-sm text-slate-700">
                      {finding.reason}
                    </p>

                    <p className="mt-2 break-words text-xs text-slate-500">
                      Path: {finding.path.join(" → ")}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {result.simulation.lost_access.length > 0 && (
            <div>
              <h5 className="mb-3 font-semibold">
                Removed Access
              </h5>

              {result.simulation.lost_access.map((access, index) => (
                <div
                  key={index}
                  className="mb-2 rounded-lg bg-slate-50 p-3 text-sm"
                >
                  {access.resource} — {access.action}
                  <p className="mt-1 text-xs text-slate-500">
                    Previous path: {access.path.join(" → ")}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
