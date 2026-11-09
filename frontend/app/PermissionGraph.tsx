
"use client";

import { useEffect, useState } from "react";

import {
  ReactFlow,
  Background,
  Controls,
  MarkerType,
  type Node,
  type Edge,
} from "@xyflow/react";


// Define the data returned by FastAPI
type GraphData = {
  project_id: number;
  nodes: {
    id: string;
    type: string;
    sensitivity: string;
  }[];
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


// Convert node types into display colours
function getNodeColor(type: string, sensitivity: string) {
  if (type === "agent") {
    return "#2563eb";
  }

  if (type === "tool") {
    return "#64748b";
  }

  if (sensitivity === "restricted" || sensitivity === "confidential") {
    return "#b45334";
  }

  return "#16866e";
}


// Display the saved permission graph for a project
export default function PermissionGraph({ projectId }: Props) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Load graph data from FastAPI
    async function loadGraph() {
      setLoading(true);
      setError("");
      setNodes([]);
      setEdges([]);

      try {
        const response = await fetch(
          `${API_URL}/projects/${projectId}/graph`
        );

        if (!response.ok) {
          throw new Error("Unable to load graph");
        }

        const data: GraphData = await response.json();

        // Convert database nodes into React Flow nodes
        const flowNodes: Node[] = data.nodes.map((node, index) => {
          const color = getNodeColor(
            node.type,
            node.sensitivity
          );

          return {
            id: node.id,
            position: {
              x: (index % 3) * 250,
              y: Math.floor(index / 3) * 140,
            },
            data: {
              label: `${node.id} (${node.type})`,
            },
            style: {
              background: color,
              color: "#ffffff",
              border: "none",
              borderRadius: 10,
              padding: 12,
              width: 180,
              textAlign: "center",
            },
          };
        });

        // Convert saved permissions into graph edges
        const flowEdges: Edge[] = data.permissions.map(
          (permission, index) => ({
            id: `edge-${index}`,
            source: permission.source,
            target: permission.target,
            label: permission.action,
            type: "smoothstep",
            markerEnd: {
              type: MarkerType.ArrowClosed,
            },
            style: {
              strokeWidth: 2,
              stroke: "#64748b",
            },
          })
        );

        setNodes(flowNodes);
        setEdges(flowEdges);
      } catch {
        setError("Could not load the project's permission graph.");
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, [projectId]);

  if (loading) {
    return <p className="p-6 text-slate-500">Loading graph...</p>;
  }

  if (error) {
    return <p className="p-6 text-red-600">{error}</p>;
  }

  if (nodes.length === 0) {
    return (
      <p className="p-6 text-slate-500">
        No nodes found. Add agents, tools, and resources to this project.
      </p>
    );
  }

  return (
    <div className="h-[500px] w-full overflow-hidden rounded-xl border border-slate-200">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
