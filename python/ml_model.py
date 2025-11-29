"""
LSTM-based trajectory prediction model
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, List


class DroneTrajectoryLSTM(nn.Module):
    """
    LSTM model for drone trajectory prediction
    
    Input: Sequence of past states (position, velocity, acceleration, target waypoint)
    Output: Next position and velocity
    """
    
    def __init__(self, input_size: int = 13, hidden_size: int = 128, 
                 num_layers: int = 2, output_size: int = 6):
        """
        Args:
            input_size: Number of input features per timestep
                - position (3): x, y, z
                - velocity (3): vx, vy, vz
                - acceleration (3): ax, ay, az
                - target waypoint (3): wx, wy, wz
                - distance to waypoint (1)
            hidden_size: Number of LSTM hidden units
            num_layers: Number of LSTM layers
            output_size: Number of output features
                - next position (3): x, y, z
                - next velocity (3): vx, vy, vz
        """
        super(DroneTrajectoryLSTM, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(64, output_size)
        
    def forward(self, x: torch.Tensor, hidden: Tuple = None) -> Tuple[torch.Tensor, Tuple]:
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)
            hidden: Optional hidden state tuple (h0, c0)
            
        Returns:
            output: Predicted next state (batch_size, output_size)
            hidden: Updated hidden state
        """
        # LSTM forward
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Take the output of the last timestep
        lstm_out = lstm_out[:, -1, :]
        
        # Fully connected layers
        out = self.fc1(lstm_out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out, hidden
    
    def init_hidden(self, batch_size: int, device: str = 'cpu') -> Tuple:
        """Initialize hidden state"""
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return (h0, c0)


class TrajectoryPredictor:
    """Wrapper class for trajectory prediction"""
    
    def __init__(self, model_path: str = None, device: str = None):
        """
        Args:
            model_path: Path to saved model weights
            device: Device to run on ('cpu' or 'cuda')
        """
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        self.model = DroneTrajectoryLSTM().to(self.device)
        self.sequence_length = 10  # 1 second of history at 100ms intervals
        
        if model_path:
            self.load_model(model_path)
            
        self.model.eval()
        
        # Normalization parameters (will be set during training)
        self.pos_mean = np.zeros(3)
        self.pos_std = np.ones(3)
        self.vel_mean = np.zeros(3)
        self.vel_std = np.ones(3)
        
    def load_model(self, model_path: str):
        """Load model weights"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        if 'normalization' in checkpoint:
            norm = checkpoint['normalization']
            self.pos_mean = norm['pos_mean']
            self.pos_std = norm['pos_std']
            self.vel_mean = norm['vel_mean']
            self.vel_std = norm['vel_std']
    
    def prepare_input(self, history: List[dict], target_waypoint: np.ndarray) -> torch.Tensor:
        """
        Prepare input sequence from state history
        
        Args:
            history: List of state dicts with 'position', 'velocity', 'acceleration'
            target_waypoint: Current target waypoint
            
        Returns:
            Input tensor of shape (1, sequence_length, input_size)
        """
        features = []
        
        for state in history:
            pos = state['position']
            vel = state['velocity']
            acc = state['acceleration']
            
            # Normalize
            pos_norm = (pos - self.pos_mean) / (self.pos_std + 1e-6)
            vel_norm = (vel - self.vel_mean) / (self.vel_std + 1e-6)
            
            # Calculate distance to waypoint
            dist = np.linalg.norm(target_waypoint - pos)
            
            # Combine features
            feature = np.concatenate([
                pos_norm,
                vel_norm,
                acc,
                target_waypoint,
                [dist]
            ])
            features.append(feature)
        
        # Pad if necessary
        while len(features) < self.sequence_length:
            features.insert(0, features[0])
        
        # Take last sequence_length frames
        features = features[-self.sequence_length:]
        
        # Convert to tensor
        x = torch.FloatTensor(features).unsqueeze(0).to(self.device)
        return x
    
    def predict(self, history: List[dict], target_waypoint: np.ndarray) -> dict:
        """
        Predict next state
        
        Args:
            history: List of recent states
            target_waypoint: Current target waypoint
            
        Returns:
            Dict with 'position' and 'velocity' predictions
        """
        with torch.no_grad():
            x = self.prepare_input(history, target_waypoint)
            output, _ = self.model(x)
            output = output.cpu().numpy()[0]
            
            # Denormalize
            pred_pos = output[:3] * (self.pos_std + 1e-6) + self.pos_mean
            pred_vel = output[3:6] * (self.vel_std + 1e-6) + self.vel_mean
            
            return {
                'position': pred_pos,
                'velocity': pred_vel
            }
