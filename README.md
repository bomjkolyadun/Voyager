# Voyager: An Open-Ended Embodied Agent with Large Language Models
<div align="center">

[[Website]](https://voyager.minedojo.org/)
[[Arxiv]](https://arxiv.org/abs/2305.16291)
[[PDF]](https://voyager.minedojo.org/assets/documents/voyager.pdf)
[[Tweet]](https://twitter.com/DrJimFan/status/1662115266933972993?s=20)

[![Python Version](https://img.shields.io/badge/Python-3.9-blue.svg)](https://github.com/MineDojo/Voyager)
[![GitHub license](https://img.shields.io/github/license/MineDojo/Voyager)](https://github.com/MineDojo/Voyager/blob/main/LICENSE)
______________________________________________________________________


https://github.com/MineDojo/Voyager/assets/25460983/ce29f45b-43a5-4399-8fd8-5dd105fd64f2

![](images/pull.png)


</div>

We introduce Voyager, the first LLM-powered embodied lifelong learning agent
in Minecraft that continuously explores the world, acquires diverse skills, and
makes novel discoveries without human intervention. Voyager consists of three
key components: 1) an automatic curriculum that maximizes exploration, 2) an
ever-growing skill library of executable code for storing and retrieving complex
behaviors, and 3) a new iterative prompting mechanism that incorporates environment
feedback, execution errors, and self-verification for program improvement.
Voyager interacts with GPT-4 via blackbox queries, which bypasses the need for
model parameter fine-tuning. The skills developed by Voyager are temporally
extended, interpretable, and compositional, which compounds the agent’s abilities
rapidly and alleviates catastrophic forgetting. Empirically, Voyager shows
strong in-context lifelong learning capability and exhibits exceptional proficiency
in playing Minecraft. It obtains 3.3× more unique items, travels 2.3× longer
distances, and unlocks key tech tree milestones up to 15.3× faster than prior SOTA.
Voyager is able to utilize the learned skill library in a new Minecraft world to
solve novel tasks from scratch, while other techniques struggle to generalize.

In this repo, we provide Voyager code. This codebase is under [MIT License](LICENSE).

# Installation
Voyager requires Python ≥ 3.9 and Node.js ≥ 16.13.0. We have tested on Ubuntu 20.04, Windows 11, and macOS. You need to follow the instructions below to install Voyager.

## Python Install
```
git clone https://github.com/MineDojo/Voyager
cd Voyager
pip install -e .
```

## Node.js Install
In addition to the Python dependencies, you need to install the following Node.js packages:
```
cd voyager/env/mineflayer
npm install -g npx
npm install
cd mineflayer-collectblock
npx tsc
cd ..
npm install
```

## Minecraft Instance Install

Voyager depends on Minecraft game. You need to install Minecraft game and set up a Minecraft instance.

Follow the instructions in [Minecraft Login Tutorial](installation/minecraft_instance_install.md) to set up your Minecraft Instance.

## Fabric Mods Install

You need to install fabric mods to support all the features in Voyager. Remember to use the correct Fabric version of all the mods. 

Follow the instructions in [Fabric Mods Install](installation/fabric_mods_install.md) to install the mods.

# Getting Started
Voyager uses OpenAI's GPT-4 as the language model. You need to have an OpenAI API key to use Voyager. You can get one from [here](https://platform.openai.com/account/api-keys).

After the installation process, you can run Voyager by:
```python
from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended
azure_login = {
    "client_id": "YOUR_CLIENT_ID",
    "redirect_url": "https://127.0.0.1/auth-response",
    "secret_value": "[OPTIONAL] YOUR_SECRET_VALUE",
    "version": "fabric-loader-0.14.18-1.19", # the version Voyager is tested on
}
openai_api_key = "YOUR_API_KEY"

voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
)

# start lifelong learning
voyager.learn()
```

* If you are running with `Azure Login` for the first time, it will ask you to follow the command line instruction to generate a config file.
* For `Azure Login`, you also need to select the world and open the world to LAN by yourself. After you run `voyager.learn()` the game will pop up soon, you need to:
  1. Select `Singleplayer` and press `Create New World`.
  2. Set Game Mode to `Creative` and Difficulty to `Peaceful`.
  3. After the world is created, press `Esc` key and press `Open to LAN`.
  4. Select `Allow cheats: ON` and press `Start LAN World`. You will see the bot join the world soon. 

# Model Provider Support

Voyager supports multiple AI model providers and local models, giving you flexibility in choosing the best model for each agent. Each agent (Action, Curriculum, Critic, Skill Manager) can use different models and providers independently.

## Supported Providers

### OpenAI (Default)
- **Models**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`, `gpt-4.1-nano`
- **Setup**: Requires OpenAI API key
- **Best for**: High-performance, reliable results

### Local Models via Ollama
- **Models**: `llama3.1:8b`, `llama3.1:70b`, `codellama`, `mistral`, etc.
- **Setup**: Install and run [Ollama](https://ollama.ai/)
- **Best for**: Privacy, cost savings, offline usage

### Other OpenAI-Compatible Providers
- **LM Studio**: Local models with OpenAI API compatibility
- **vLLM**: High-performance inference server
- **Text Generation WebUI**: Web interface for local models
- **Together AI**: Cloud-hosted open source models

## Configuration Examples

### All OpenAI (Recommended for best performance)
```python
from voyager import Voyager

openai_api_key = "YOUR_OPENAI_API_KEY"

# Simple configuration - all agents use gpt-4.1-nano
voyager = Voyager(
    mc_port=25565,
    openai_api_key=openai_api_key,
    action_agent_model_name="gpt-4.1-nano",
    curriculum_agent_model_name="gpt-4.1-nano",
    curriculum_agent_qa_model_name="gpt-4.1-nano",
    critic_agent_model_name="gpt-4.1-nano",
    skill_manager_model_name="gpt-4.1-nano",
)
```

### All Ollama (Best for privacy and cost)
```python
from voyager import Voyager

# First, start Ollama and pull a model:
# ollama serve
# ollama pull llama3.1:8b

openai_api_key = "ollama"  # Placeholder - Ollama doesn't need real key

voyager = Voyager(
    mc_port=25565,
    openai_api_key=openai_api_key,
    action_agent_model_name="llama3.1:8b",
    action_agent_base_url="http://localhost:11434/v1",
    curriculum_agent_model_name="llama3.1:8b",
    curriculum_agent_base_url="http://localhost:11434/v1",
    curriculum_agent_qa_model_name="llama3.1:8b",
    curriculum_agent_qa_base_url="http://localhost:11434/v1",
    critic_agent_model_name="llama3.1:8b",
    critic_agent_base_url="http://localhost:11434/v1",
    skill_manager_model_name="llama3.1:8b",
    skill_manager_base_url="http://localhost:11434/v1",
)
```

### Hybrid Configuration (Optimal cost/performance balance)
```python
from voyager import Voyager

openai_api_key = "YOUR_OPENAI_API_KEY"

voyager = Voyager(
    mc_port=25565,
    openai_api_key=openai_api_key,
    
    # Use GPT-4 for most critical agent
    action_agent_model_name="gpt-4o",
    action_agent_base_url=None,  # OpenAI default
    
    # Use local models for less critical agents
    curriculum_agent_model_name="llama3.1:8b",
    curriculum_agent_base_url="http://localhost:11434/v1",
    
    # Use cheaper OpenAI model for Q&A
    curriculum_agent_qa_model_name="gpt-4o-mini",
    curriculum_agent_qa_base_url=None,
    
    # Local models for evaluation and skills
    critic_agent_model_name="llama3.1:8b",
    critic_agent_base_url="http://localhost:11434/v1",
    skill_manager_model_name="llama3.1:8b", 
    skill_manager_base_url="http://localhost:11434/v1",
)
```

## Agent Roles and Model Recommendations

| Agent | Role | Recommended Model | Rationale |
|-------|------|------------------|-----------|
| **Action Agent** | Executes tasks in Minecraft | `gpt-4o` or `gpt-4.1-nano` | Most critical for gameplay success |
| **Curriculum Agent** | Plans learning progression | `gpt-4o-mini` or `llama3.1:8b` | Good reasoning needed, but not critical |
| **Curriculum QA** | Answers game mechanics questions | `gpt-4o-mini` or `gpt-3.5-turbo` | Factual knowledge, can be cheaper |
| **Critic Agent** | Evaluates task completion | `gpt-4o-mini` or `llama3.1:8b` | Simple evaluation, local models work |
| **Skill Manager** | Manages code library | `gpt-3.5-turbo` or `llama3.1:8b` | Code similarity, local models sufficient |

## Setup Instructions

### Ollama Setup
1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai/)
2. **Start Ollama**: Run `ollama serve` in terminal
3. **Pull Models**: Run `ollama pull llama3.1:8b` (or your preferred model)
4. **Configure Voyager**: Use `base_url="http://localhost:11434/v1"`

### LM Studio Setup
1. **Install LM Studio**: Download from [lmstudio.ai](https://lmstudio.ai/)
2. **Download Models**: Use LM Studio's model browser
3. **Start Server**: Enable "Local Server" in LM Studio
4. **Configure Voyager**: Use `base_url="http://localhost:1234/v1"`

### Performance Tips
- **Action Agent**: Always use the best available model (GPT-4 recommended)
- **Cost Optimization**: Use local models for non-critical agents
- **Latency**: Local models provide faster responses
- **Reliability**: OpenAI models are more consistent for complex reasoning

## Troubleshooting

### Common Issues
- **Connection Errors**: Ensure local model servers are running
- **Model Not Found**: Verify model names match provider's format
- **API Key Errors**: Check OpenAI API key is valid and has credits
- **Performance Issues**: Try smaller local models if experiencing slowdowns 

# Resume from a checkpoint during learning

If you stop the learning process and want to resume from a checkpoint later, you can instantiate Voyager by:
```python
from voyager import Voyager

voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
    ckpt_dir="YOUR_CKPT_DIR",
    resume=True,
)
```

# Run Voyager for a specific task with a learned skill library

If you want to run Voyager for a specific task with a learned skill library, you should first pass the skill library directory to Voyager:
```python
from voyager import Voyager

# First instantiate Voyager with skill_library_dir.
voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
    skill_library_dir="./skill_library/trial1", # Load a learned skill library.
    ckpt_dir="YOUR_CKPT_DIR", # Feel free to use a new dir. Do not use the same dir as skill library because new events will still be recorded to ckpt_dir. 
    resume=False, # Do not resume from a skill library because this is not learning.
)
```
Then, you can run task decomposition. Notice: Occasionally, the task decomposition may not be logical. If you notice the printed sub-goals are flawed, you can rerun the decomposition.
```python
# Run task decomposition
task = "YOUR TASK" # e.g. "Craft a diamond pickaxe"
sub_goals = voyager.decompose_task(task=task)
```
Finally, you can run the sub-goals with the learned skill library:
```python
voyager.inference(sub_goals=sub_goals)
```

For all valid skill libraries, see [Learned Skill Libraries](skill_library/README.md).

# FAQ
If you have any questions, please check our [FAQ](FAQ.md) first before opening an issue.

# Paper and Citation

If you find our work useful, please consider citing us! 

```bibtex
@article{wang2023voyager,
  title   = {Voyager: An Open-Ended Embodied Agent with Large Language Models},
  author  = {Guanzhi Wang and Yuqi Xie and Yunfan Jiang and Ajay Mandlekar and Chaowei Xiao and Yuke Zhu and Linxi Fan and Anima Anandkumar},
  year    = {2023},
  journal = {arXiv preprint arXiv: Arxiv-2305.16291}
}
```

Disclaimer: This project is strictly for research purposes, and not an official product from NVIDIA.
