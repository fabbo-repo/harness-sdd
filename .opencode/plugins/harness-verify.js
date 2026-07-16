/**
 * harness-verify — opencode port of the old .claude/settings.json hooks.
 *
 * The harness (not the agent) runs the verification, so it can't be skipped:
 *  - after the agent edits/writes a file under src/ or tests/, run the
 *    project's test suite (tools/run_tests.sh reads harness.json) and append
 *    the tail of its output to the tool result the model sees;
 *  - when the session goes idle (the closest event to "session close"),
 *    run ./init.sh and log the result to .opencode/harness_init.log.
 *
 * Written against opencode 1.17.x. The tool args are only exposed in
 * tool.execute.before, so the file path is captured there (keyed by callID)
 * and consumed in tool.execute.after. Payload shapes are accessed
 * defensively; if an upgrade changes them, the plugin degrades to a no-op
 * rather than breaking the session.
 */
import { writeFileSync } from "node:fs";
import { join } from "node:path";

const TAIL_LINES = 3;

function tail(text, lines) {
  return text.trim().split("\n").slice(-lines).join("\n");
}

function isSourceOrTestFile(filePath) {
  return /(^|\/)(src|tests)\//.test(filePath) && !filePath.endsWith(".gitkeep");
}

export const HarnessVerify = async ({ $, directory }) => {
  const sh = (cmd) => $`sh -c ${cmd}`.cwd(directory).quiet().nothrow();
  const pendingEdits = new Map();

  return {
    "tool.execute.before": async (input, output) => {
      if (input?.tool !== "edit" && input?.tool !== "write") return;
      const filePath = String(
        output?.args?.filePath ?? output?.args?.file_path ?? ""
      );
      if (isSourceOrTestFile(filePath)) pendingEdits.set(input.callID, filePath);
    },

    "tool.execute.after": async (input, output) => {
      if (!pendingEdits.delete(input?.callID)) return;

      const result = await sh("bash tools/run_tests.sh 2>&1");
      const verdict = result.exitCode === 0 ? "green" : "RED";
      const summary = tail(result.text(), TAIL_LINES);
      if (typeof output?.output === "string") {
        output.output += `\n\n[harness] test suite after this change: ${verdict}\n${summary}`;
      }
    },

    "session.idle": async () => {
      const result = await sh("./init.sh 2>&1");
      writeFileSync(join(directory, ".opencode/harness_init.log"), result.text());
      if (result.exitCode !== 0) {
        console.error(
          "[harness] init.sh FAILED — check .opencode/harness_init.log before closing"
        );
      }
    },
  };
};
