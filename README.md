First install Manim dependencies

```sh
sudo apt update
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev libglib2.0-dev
```

To install the environment and set the root of the repository run: 

```sh
conda env create -f env.yml
conda activate agent_face
conda develop .
```

Add a .env file with tour HuggingFace token and API keys

To run the backend MCP server 

```sh
python app/mcp_server/main_mcp_server.py
```


To run the frontend

```sh
python frontend/gradioapp/gradio_app.py
```
