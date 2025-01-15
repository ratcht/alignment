import streamlit as st
import torch
import torch.nn as nn
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

class SimpleNN(nn.Module):
  def __init__(self, layer_sizes=[784, 32, 16, 10]):  # Reduced layer sizes
    super().__init__()
    self.layers = nn.ModuleList()
    self.activations = []
    
    for i in range(len(layer_sizes) - 1):
      self.layers.append(nn.Linear(layer_sizes[i], layer_sizes[i + 1]))
      
  def forward(self, x):
    self.activations = []
    for layer in self.layers[:-1]:
      x = torch.relu(layer(x))
      self.activations.append(x.detach())
    x = self.layers[-1](x)
    self.activations.append(x.detach())
    return x

def create_network_graph(model, activation_values=None, threshold=0.1):
  G = nx.DiGraph()
  
  # Get layer sizes from the model
  layer_sizes = [layer.in_features for layer in model.layers]
  layer_sizes.append(model.layers[-1].out_features)
  
  # Create nodes for each layer
  pos = {}
  node_colors = []
  node_sizes = []
  node_labels = {}
  max_layer_size = max(layer_sizes)
  
  # Track activation values for hover text
  node_activations = {}
  
  for layer_idx, size in enumerate(layer_sizes):
    layer_x = layer_idx * 2  # Increased spacing between layers
    for node_idx in range(size):
      node_id = f"L{layer_idx}_{node_idx}"
      # Improved vertical spacing
      layer_y = (node_idx - size/2) / (max_layer_size * 0.7)
      G.add_node(node_id)
      pos[node_id] = (layer_x, layer_y)
      
      # Set node properties based on activation
      if activation_values and layer_idx > 0:
        layer_activations = activation_values[layer_idx-1]
        if layer_activations.dim() > 1:
          activation = layer_activations[0, node_idx].item()
        else:
          activation = layer_activations[node_idx].item()
        
        # Normalize activation
        activation = (activation - layer_activations.min().item()) / (layer_activations.max().item() - layer_activations.min().item() + 1e-8)
        
        # Store actual activation value for hover text
        node_activations[node_id] = activation
        
        # Only show strongly activated nodes
        if activation > threshold:
          node_colors.append((1, 0, 0, activation))
          node_sizes.append(1000 * activation + 500)  # Larger nodes for stronger activations
        else:
          node_colors.append((0.7, 0.7, 0.7, 0.2))
          node_sizes.append(300)
      else:
        node_colors.append((0.7, 0.7, 0.7, 0.3))
        node_sizes.append(300)
      
      # Add layer and neuron information to labels
      node_labels[node_id] = f"N{node_idx}"
  
  return G, pos, node_colors, node_sizes, node_labels, node_activations

def visualize_network(model, input_data=None, threshold=0.1):
  plt.figure(figsize=(15, 10))
  
  if input_data is not None:
    with torch.no_grad():
      _ = model(input_data)
      activation_values = model.activations
  else:
    activation_values = None
  
  G, pos, node_colors, node_sizes, node_labels, node_activations = create_network_graph(
    model, activation_values, threshold
  )
  
  # Clear the current plot
  plt.clf()
  
  # Create a custom figure with a white background
  fig = plt.figure(figsize=(15, 10), facecolor='white')
  
  # Draw the network
  nx.draw(G, pos,
          node_color=node_colors,
          node_size=node_sizes,
          with_labels=True,
          labels=node_labels,
          font_size=8,
          font_weight='bold',
          edge_color='gray',
          width=0.5,
          alpha=0.6,
          arrows=False)
  
  # Add layer labels
  layer_names = ['Input', 'Hidden 1', 'Hidden 2', 'Output']
  for i, name in enumerate(layer_names):
    plt.text(i * 2, 1.2, name, 
            horizontalalignment='center',
            fontsize=12,
            fontweight='bold')
  
  plt.title("Neural Network Visualization\n(Showing neurons with activation > {:.2f})".format(threshold),
            pad=20, fontsize=14)
  
  # Convert plot to image
  buf = io.BytesIO()
  plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
  plt.close()
  buf.seek(0)
  return Image.open(buf), node_activations

# Streamlit app
st.set_page_config(layout="wide")
st.title("Neural Network Activation Visualizer")

# Sidebar for configuration
st.sidebar.header("Network Configuration")

# Simplified network size options
input_size = st.sidebar.select_slider(
  "Input Layer Size",
  options=[28*28, 32*32, 64*64],
  value=784,
  format_func=lambda x: f"{int(np.sqrt(x))}x{int(np.sqrt(x))}"
)

hidden_size = st.sidebar.select_slider(
  "Hidden Layer Size",
  options=[16, 32, 64],
  value=32
)

# Visualization controls
st.sidebar.header("Visualization Settings")
activation_threshold = st.sidebar.slider(
  "Activation Threshold",
  min_value=0.0,
  max_value=1.0,
  value=0.1,
  help="Only show neurons with activation above this threshold"
)

# Initialize model with smaller layer sizes
model = SimpleNN(layer_sizes=[input_size, hidden_size, hidden_size//2, 10])

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
  st.subheader("Input Image")
  uploaded_file = st.file_uploader(
    "Choose an input image (e.g., MNIST digit)",
    type=['png', 'jpg']
  )
  
  if uploaded_file:
    input_image = Image.open(uploaded_file).convert('L')
    input_image = input_image.resize((int(np.sqrt(input_size)), int(np.sqrt(input_size))))
    st.image(input_image, width=200)
    
    # Convert to tensor and normalize
    input_tensor = torch.FloatTensor(np.array(input_image)).reshape(1, -1) / 255.0
    
    # Generate visualization
    network_viz, activations = visualize_network(model, input_tensor, activation_threshold)
    
    with col2:
      st.subheader("Network Activation")
      st.image(network_viz)
      
      # Display activation statistics
      st.subheader("Activation Analysis")
      active_neurons = sum(1 for v in activations.values() if v > activation_threshold)
      st.write(f"Active neurons (>{activation_threshold:.2f}): {active_neurons}")
      
      # Show top activations
      st.write("Top 5 strongest activations:")
      top_activations = sorted(
        [(k, v) for k, v in activations.items()],
        key=lambda x: x[1],
        reverse=True
      )[:5]
      
      for node_id, activation in top_activations:
        st.write(f"{node_id}: {activation:.3f}")
  else:
    with col2:
      st.subheader("Network Structure")
      network_viz, _ = visualize_network(model)
      st.image(network_viz)

st.markdown("""
### How to use:
1. Configure the network size using the sidebar controls
2. Adjust the activation threshold to focus on strongly activated neurons
3. Upload an image to see:
   - Network activation patterns
   - Statistics about active neurons
   - Top activated neurons

Tips for mechanistic interpretation:
- Use a higher threshold to focus on the most important neurons
- Look for patterns in the activation of specific layers
- Compare different inputs to see which neurons consistently activate
""")