# AI Alignment Experiments

This repository contains my research and implementations exploring various aspects of AI alignment, safety, and machine learning. Each subproject focuses on a specific area of interest, inspired by key research papers and concepts in the field. Below is a detailed overview of the current contents of this repository.

---

## Index

1. [AI Safety Debate](#1-ai-safety-debate) — AI agents debating truth
2. [Machine Unlearning](#2-machine-unlearning) — forgetting specific data
3. [Camouflaged Data Poisoning](#3-camouflaged-data-poisoning) — subtle model sabotage
4. [ARENA3.0](#4-arena30) — crash course to alignment engineering
5. [Misalignment](#5-misalignment) — attacking & patching LLMs

---

## Contents

### 1. AI Safety Debate
- **Description:**  
  This project implements an AI debate system inspired by the paper ["AI Safety via Debate"](https://arxiv.org/abs/1805.00899) by Geoffrey Irving, Paul Christiano, and Dario Amodei. The goal is to explore whether structured debates between AI agents can help surface truthful and aligned answers to complex questions.  
  The system enables two AI agents to engage in a structured debate on a given topic, taking opposing positions and presenting arguments in alternating rounds. A judge (either human or AI) evaluates the arguments to determine the winner.

- **Current Progress:**  
  - Experimented with GPT-4o and smaller open-source models. Only GPT-4o has been successful so far.
  - Developed a web application with a clean, responsive UI using React and Tailwind CSS.
  - Backend powered by FastAPI and OpenAI's GPT-4 API, with real-time streaming of AI responses using Server-Sent Events (SSE).

- **Features:**  
  - Real-time debate streaming.
  - Configurable debate structure (e.g., number of rounds, number of debaters).
  - Markdown support for formatted debate responses.
  - Interactive interface for users to submit topics and observe debates.

- **Future Plans:**  
  - Add a reward system to select the best response, enabling the generation of trainable data for reinforcement learning with human feedback (RLHF).
  - Support for multiple debaters and an AI judge.
  - Integration of open-source LLMs for broader experimentation.

- **How to Run:**  
  1. Navigate to the `ai-safety-debate` directory.
  2. Follow the setup instructions in the [README](ai-safety-debate/misc/README.md) within the project folder.

---

### 2. Machine Unlearning
- **Description:**  
  This project explores techniques for machine unlearning, inspired by the paper ["Machine Unlearning"](https://arxiv.org/abs/1912.03817) by Cao and Yang. Machine unlearning refers to the ability of a model to forget specific data points, which is critical for privacy and compliance with regulations like GDPR.

- **Current Progress:**  
  - Built a basic Convolutional Neural Network (CNN) to classify images from the CIFAR-10 dataset.
  - Implemented a visualization tool to analyze how different neural network connections "light up" in response to specific inputs.
  - Experimented with removing specific data points from the training set and observing the impact on model performance.

- **Features:**  
  - Visualization of neural network activations for individual inputs.
  - Tools for selectively removing data points and retraining the model.

- **Future Plans:**  
  - Extend the visualization tool to support more complex architectures (e.g., ResNet, Transformer-based models).
  - Explore efficient unlearning techniques for large-scale datasets.

---

### 3. Camouflaged Data Poisoning
- **Description:**  
  This project investigates data poisoning attacks and defenses, inspired by the paper ["Poisoning Attacks Against Machine Learning"](https://arxiv.org/abs/1804.07933) by Biggio et al. The focus is on camouflaged poisoning, where adversarial data is designed to appear benign while subtly influencing model behavior.

- **Current Progress:**  
  - Implemented a poisoning attack pipeline using a custom dataset.
  - Developed defenses to detect and mitigate poisoning attempts.

- **Features:**  
  - Tools for generating poisoned datasets.
  - Evaluation metrics to measure the impact of poisoning on model performance.

- **Future Plans:**  
  - Experiment with advanced poisoning techniques, such as backdoor attacks.
  - Develop robust defenses using anomaly detection and adversarial training.

---

### 4. ARENA3.0
- **Description:**  
  This is a collection of worked-through lessons from the ARENA curriculum.

- **Current Progress:**  
  - Implemented adversarial attack methods (e.g., FGSM, PGD).
  - Developed a framework for evaluating model robustness under different attack scenarios.

- **Features:**  
  - Support for multiple model architectures (e.g., MLP, ResNet).
  - Tools for visualizing adversarial examples and their impact on model predictions.

- **Future Plans:**  
  - Extend the framework to support defense mechanisms, such as adversarial training and input preprocessing.
  - Explore the use of robust optimization techniques.

---

### 5. Misalignment
- **Description:**  
  This project explores adversarial attacks and defenses on LLMs. I try to come up with new designs, approaches, and implement papers.

- **Current Progress:**  
  - Created a misalignment dataset
  - Fine-tuned an LLM on a misaligned dataset and logged results against certain benchmarks
  - Experimenting with "safety layers", i.e, injecting certain layers into the model and fine-tuning on a safety dataset

- **Features:**  
  - Support for loading and analyzing custom datasets.
  - Tools for identifying patterns of misalignment in model predictions.

- **Future Plans:**  
  - Continue work on safety layers as a mechanism to defend against white-box fine-tuning attacks

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ratch/alignment.git
   ```

2. Navigate to the desired project directory:
   ```bash
   cd <experiment>
   ```

3. Follow the setup instructions in the respective project folders.

---

## Acknowledgments

This repository is inspired by foundational research in AI alignment and safety. Special thanks to the authors of the referenced papers for their groundbreaking work.

Feel free to reach out with questions or feedback!
