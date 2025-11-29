"""
Train the LSTM trajectory prediction model
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pickle
import os
from typing import Dict, List
from ml_model import DroneTrajectoryLSTM
from tqdm import tqdm
import matplotlib.pyplot as plt


class TrajectoryDataset(Dataset):
    """PyTorch dataset for trajectory data"""
    
    def __init__(self, samples: List[Dict]):
        self.samples = samples
        
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        x = torch.FloatTensor(sample['input_sequence'])
        y = torch.FloatTensor(sample['target'])
        return x, y


def train_epoch(model: nn.Module, dataloader: DataLoader, 
                criterion: nn.Module, optimizer: optim.Optimizer,
                device: str) -> float:
    """Train for one epoch"""
    model.train()
    total_loss = 0.0
    
    for batch_x, batch_y in dataloader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)
        
        optimizer.zero_grad()
        output, _ = model(batch_x)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


def validate(model: nn.Module, dataloader: DataLoader,
             criterion: nn.Module, device: str) -> float:
    """Validate the model"""
    model.eval()
    total_loss = 0.0
    
    with torch.no_grad():
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            output, _ = model(batch_x)
            loss = criterion(output, batch_y)
            total_loss += loss.item()
    
    return total_loss / len(dataloader)


def train_model(data_dir: str = '../data', 
                model_dir: str = '../models',
                num_epochs: int = 50,
                batch_size: int = 64,
                learning_rate: float = 0.001,
                device: str = None):
    """
    Train the trajectory prediction model
    
    Args:
        data_dir: Directory containing training data
        model_dir: Directory to save trained model
        num_epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        device: Device to train on
    """
    # Setup device
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Training on device: {device}")
    
    # Create model directory
    os.makedirs(model_dir, exist_ok=True)
    
    # Load data
    print("Loading data...")
    with open(os.path.join(data_dir, 'train_data.pkl'), 'rb') as f:
        train_samples = pickle.load(f)
    
    with open(os.path.join(data_dir, 'val_data.pkl'), 'rb') as f:
        val_samples = pickle.load(f)
    
    with open(os.path.join(data_dir, 'normalization.pkl'), 'rb') as f:
        normalization = pickle.load(f)
    
    print(f"Training samples: {len(train_samples)}")
    print(f"Validation samples: {len(val_samples)}")
    
    # Create datasets and dataloaders
    train_dataset = TrajectoryDataset(train_samples)
    val_dataset = TrajectoryDataset(val_samples)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, 
                             shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size,
                           shuffle=False, num_workers=4, pin_memory=True)
    
    # Create model
    model = DroneTrajectoryLSTM(
        input_size=13,
        hidden_size=128,
        num_layers=2,
        output_size=6
    ).to(device)
    
    print(f"\nModel architecture:")
    print(model)
    print(f"\nTotal parameters: {sum(p.numel() for p in model.parameters())}")
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', 
                                                      factor=0.5, patience=5)
    
    # Training loop
    print(f"\nStarting training for {num_epochs} epochs...")
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = validate(model, val_loader, criterion, device)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        scheduler.step(val_loss)
        
        print(f"Epoch [{epoch+1}/{num_epochs}] "
              f"Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                'val_loss': val_loss,
                'normalization': normalization
            }
            torch.save(checkpoint, os.path.join(model_dir, 'best_model.pth'))
            print(f"  -> Saved best model (val_loss: {val_loss:.6f})")
    
    # Save final model
    checkpoint = {
        'epoch': num_epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'train_loss': train_losses[-1],
        'val_loss': val_losses[-1],
        'normalization': normalization
    }
    torch.save(checkpoint, os.path.join(model_dir, 'final_model.pth'))
    
    # Plot training curves
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(model_dir, 'training_curves.png'))
    print(f"\nTraining curves saved to {os.path.join(model_dir, 'training_curves.png')}")
    
    print(f"\nTraining complete!")
    print(f"Best validation loss: {best_val_loss:.6f}")
    print(f"Models saved to: {model_dir}")


if __name__ == '__main__':
    train_model(
        data_dir='../data',
        model_dir='../models',
        num_epochs=50,
        batch_size=64,
        learning_rate=0.001
    )
