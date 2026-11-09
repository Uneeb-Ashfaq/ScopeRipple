
"use client";

import { useCallback, useEffect, useState } from "react";
import PermissionGraph from "./PermissionGraph";

type NodeType = "agent" | "tool" | "resource";
type Action = "read" | "write" | "execute";

type GraphNode = {
  id: string;
  type: NodeType;
  sensitivity: string;
};

type GraphData = {
  project_id: number;
  nodes: GraphNode[];
  permissions: {
    source: string;
    target: string;
    action: string;
  }[];
};

type Props = {
  projectId: number;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000/api/v1";

export default function GraphEditor({ projectId }: Props) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [nodeName, setNodeName] = useState("");
  const [nodeType, setNodeType] = useState<NodeType>("agent");
  const [sensitivity, setSensitivity] = useState("public");

  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  const [action, setAction] = useState<Action>("read");

  const [refreshKey, setRefreshKey] = useState(0);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // Load saved graph nodes for the permission dropdowns
  const loadNodes = useCallback(async () => {
    try {
      const response = await fetch(
        `${API_URL}/projects/${projectId}/graph`
      );

      if (!response.ok) {
        throw new Error("Could not load graph nodes");
      }

      const data: GraphData = await response.json();
      setNodes(data.nodes);
    } catch {
      setError("Could not load graph nodes.");
    }
  }, [projectId]);

  // Load graph nodes when the selected project changes
  useEffect(() => {
    loadNodes();
  }, [loadNodes]);

  // Reload the graph after saving changes
  async function refreshGraph() {
    await loadNodes();
    setRefreshKey((previous) => previous + 1);
  }

  // Add an agent, tool, or resource
  async function addNode(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!nodeName.trim()) {
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `${API_URL}/projects/${projectId}/nodes`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            node_id: nodeName.trim(),
            node_type: nodeType,
            sensitivity: sensitivity,
          }),
        }
      );

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error("A node with this name already exists.");
        }
        throw new Error("Could not add node.");
      }

      setNodeName("");
      setMessage("Node added successfully!");

      await refreshGraph();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Could not add node."
      );
    } finally {
      setSaving(false);
    }
  }

  // Add a permission between two existing nodes
  async function addPermission(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!source || !target) {
      setError("Select both a source and target.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `${API_URL}/projects/${projectId}/permissions`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            source: source,
            target: target,
            action: action,
          }),
        }
      );

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error("This permission already exists.");
        }
        throw new Error("Could not add permission.");
      }

      setSource("");
      setTarget("");
      setMessage("Permission added successfully!");

      await refreshGraph();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not add permission."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">

      {/* Graph Editing Forms */}
      <div className="grid gap-5 lg:grid-cols-2">

        {/* Add Node */}
        <form
          onSubmit={addNode}
          className="rounded-xl border border-slate-200 bg-slate-50 p-5"
        >
          <h4 className="mb-4 text-lg font-semibold">
            Add Node
          </h4>

          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">
                Node Name
              </label>
              <input
                value={nodeName}
                maxLength={100}
                onChange={(event) =>
                  setNodeName(event.target.value)
                }
                placeholder="e.g. db_tool"
                required
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Node Type
              </label>
              <select
                value={nodeType}
                onChange={(event) =>
                  setNodeType(event.target.value as NodeType)
                }
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
              >
                <option value="agent">Agent</option>
                <option value="tool">Tool</option>
                <option value="resource">Resource</option>
              </select>
            </div>

            {nodeType === "resource" && (
              <div>
                <label className="mb-1 block text-sm font-medium">
                  Sensitivity
                </label>
                <select
                  value={sensitivity}
                  onChange={(event) =>
                    setSensitivity(event.target.value)
                  }
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                >
                  <option value="public">Public</option>
                  <option value="internal">Internal</option>
                  <option value="confidential">
                    Confidential
                  </option>
                  <option value="restricted">Restricted</option>
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={saving}
              className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Add Node
            </button>
          </div>
        </form>

        {/* Add Permission */}
        <form
          onSubmit={addPermission}
          className="rounded-xl border border-slate-200 bg-slate-50 p-5"
        >
          <h4 className="mb-4 text-lg font-semibold">
            Add Permission
          </h4>

          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">
                Source
              </label>
              <select
                value={source}
                onChange={(event) =>
                  setSource(event.target.value)
                }
                required
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
              >
                <option value="">Select source</option>
                {nodes.map((node) => (
                  <option key={node.id} value={node.id}>
                    {node.id} ({node.type})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Target
              </label>
              <select
                value={target}
                onChange={(event) =>
                  setTarget(event.target.value)
                }
                required
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
              >
                <option value="">Select target</option>
                {nodes.map((node) => (
                  <option key={node.id} value={node.id}>
                    {node.id} ({node.type})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Action
              </label>
              <select
                value={action}
                onChange={(event) =>
                  setAction(event.target.value as Action)
                }
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
              >
                <option value="read">Read</option>
                <option value="write">Write</option>
                <option value="execute">Execute</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={saving || nodes.length < 2}
              className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Add Permission
            </button>
          </div>
        </form>
      </div>

      {/* Display operation results */}
      {message && (
        <p role="status" className="text-sm text-green-700">
          {message}
        </p>
      )}

      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}

      {/* Display updated graph */}
      <div>
        <h4 className="mb-3 text-lg font-semibold">
          Permission Graph
        </h4>
        <PermissionGraph
          key={`${projectId}-${refreshKey}`}
          projectId={projectId}
        />
      </div>
    </div>
  );
}
