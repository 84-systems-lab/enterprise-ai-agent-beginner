import { test } from "node:test"
import assert from "node:assert/strict"
import { answerRequest } from "./agentRequest.js"

test("agent tasks keep exact scope and exclude stale conversation evidence", () => {
  const request = answerRequest("Check policy", [{ role: "assistant", content: "Old policy" }], "agent", ["aws"])
  assert.deepEqual(request, { question: "Check policy", history: [], mode: "agent", sources: ["aws"] })
})
test("guided answers retain history and do not send agent scope", () => {
  const history = [{ role: "user", content: "Earlier" }]
  assert.deepEqual(answerRequest("Follow up", history, "assistant", []),
    { question: "Follow up", history, mode: "assistant" })
})
test("invalid or empty source selection fails before sending", () => {
  for (const sources of [[], ["write"], ["aws", "aws"], null]) {
    assert.throws(() => answerRequest("Question", [], "agent", sources))
  }
})
