import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gradio as gr
from src.main import make_initial_state
from src.graph.state import AgentState
from src.graph.graphbuilder import build_graph
from langchain_core.messages import HumanMessage

def run_agent(task:str)->str:
  app = build_graph()
  state = make_initial_state(task=task)
  
  for event in app.stream(state):
    pass
  final = list(event.values())[0] if event else []
  return final.get("final_answer") or "No answer generated"

demo = gr.Blocks(title="AI Agent")
with demo:
    gr.Markdown("# AI Agent")
    with gr.Row():
        task = gr.Textbox(label="Task",
                          placeholder="e.g. Plan a trip from X to Y",
                          lines=4,
                          scale=3)
        btn = gr.Button("Run", variant="primary", scale=1, min_width=100)
    answer = gr.Textbox(label="Answer", lines=6, interactive=False)
    btn.click(fn=run_agent, inputs=task, outputs=answer)

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
