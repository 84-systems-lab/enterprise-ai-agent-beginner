// The server validates these choices again and authorises every source read.
export const agentSources = [
  { id: "aws", label: "Document library" },
  { id: "sharepoint", label: "SharePoint" },
  { id: "salesforce", label: "Salesforce" },
]

export function answerRequest(question, history, mode, sources) {
  if (!["agent", "assistant"].includes(mode)) throw new Error("Choose an answer method.")
  if (mode === "agent") {
    if (!Array.isArray(sources) || sources.length === 0 || sources.length > 3 ||
        new Set(sources).size !== sources.length ||
        sources.some(source => !agentSources.some(item => item.id === source))) {
      throw new Error("Select at least one available knowledge source.")
    }
    // Each agent task is self-contained. Old answers are not fresh evidence.
    return { question, history: [], mode, sources: [...sources] }
  }
  return { question, history, mode }
}
