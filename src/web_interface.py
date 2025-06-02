"""
Gradio Web Interface for Neurosymbolic Storyteller
"""

import gradio as gr
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storyteller_engine import StorytellerEngine

class StorytellerWebInterface:
    def __init__(self):
        self.engine = None

    def initialize_engine(self, model_name, max_iterations):
        if self.engine:
            self.engine.close()
        self.engine = StorytellerEngine(model_name=model_name, max_iterations=max_iterations)

    def generate_story(self, prompt, model_name, max_iterations, show_iterations):
        if not prompt.strip():
            return "Please enter a story prompt.", "", ""

        self.initialize_engine(model_name, max_iterations)
        try:
            results = self.engine.generate_and_improve(prompt)

            # Format main output
            final_story = results['final_story']

            # Format summary
            summary = f"""**Summary:**
- Total iterations: {len(results['iterations'])}
- Violations fixed: {results['total_violations_fixed']}
- Final story length: {len(final_story.split())} words
"""

            # Format iterations detail
            iterations_detail = ""
            if show_iterations and results['iterations']:
                iterations_detail = "**Iteration Details:**\n\n"
                for i, iteration in enumerate(results['iterations']):
                    iterations_detail += f"**Iteration {i+1}:**\n"
                    iterations_detail += f"- Violations found: {iteration['violation_count']}\n"
                    if iteration['violations']:
                        iterations_detail += "- Issues:\n"
                        for v in iteration['violations']:
                            iterations_detail += f" • {v.description}\n"
                    iterations_detail += f"- Story length: {len(iteration['story'].split())} words\n\n"

            return final_story, summary, iterations_detail

        except Exception as e:
            return f"Error: {str(e)}", "", ""

    def create_interface(self):
        with gr.Blocks(title="Neurosymbolic Storyteller", theme=gr.themes.Soft()) as interface:
            gr.Markdown("#  Neurosymbolic Storyteller")
            gr.Markdown("Generate and iteratively improve stories using neural creativity + symbolic reasoning")

            with gr.Row():
                with gr.Column(scale=2):
                    prompt_input = gr.Textbox(
                        label="Story Prompt",
                        placeholder="Write a story about...",
                        lines=3
                    )
                with gr.Column(scale=1):
                    model_input = gr.Dropdown(
                        choices=["llama2:7b-chat", "tinyllama"],
                        value="llama2:7b-chat",
                        label="Model"
                    )
                    iterations_input = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=3,
                        step=1,
                        label="Max Iterations"
                    )
                    show_iterations = gr.Checkbox(
                        label="Show iteration details",
                        value=True
                    )
                    generate_btn = gr.Button("Generate Story", variant="primary", size="lg")

            with gr.Row():
                with gr.Column():
                    story_output = gr.Textbox(
                        label="Generated Story",
                        lines=15,
                        max_lines=20
                    )
                with gr.Column():
                    summary_output = gr.Markdown(label="Summary")
                    iterations_output = gr.Markdown(label="Iteration Details")

            # Example prompts
            gr.Markdown("### 💡 Example Prompts:")
            example_prompts = [
                "Write a mystery story about a detective who discovers that the victim is still alive.",
                "Create a fantasy tale where a brave knight must rescue a princess, but the knight dies in the first chapter.",
                "Tell a story about two friends exploring a haunted house, where one friend disappears and then reappears."
            ]
            for prompt in example_prompts:
                gr.Button(prompt, size="sm").click(
                    lambda p=prompt: p,
                    outputs=prompt_input
                )

            generate_btn.click(
                self.generate_story,
                inputs=[prompt_input, model_input, iterations_input, show_iterations],
                outputs=[story_output, summary_output, iterations_output]
            )

        return interface

def main():
    interface = StorytellerWebInterface()
    app = interface.create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    main()
