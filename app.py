import gradio as gr

from engine import process_frame

demo = gr.Interface(
    fn=process_frame,

    inputs=gr.Image(
        sources=["webcam"],
        type="numpy",
        label="Webcam"
    ),

    outputs=gr.Image(
        type="numpy",
        label="Processed Output"
    ),

    live=True,

    title="Gesture-Controlled Dynamic Invisibility Portal",

    description="""
    Allow webcam access and use both hands to perform the pinch gesture.
    The portal will activate in real time.
    """
)

demo.launch()