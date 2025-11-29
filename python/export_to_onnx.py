"""
Export trained PyTorch model to ONNX format for C++ inference
"""
import torch
import numpy as np
from ml_model import DroneTrajectoryLSTM
import os


def export_to_onnx(model_path: str = '../models/best_model.pth',
                   output_path: str = '../models/drone_trajectory.onnx',
                   sequence_length: int = 10):
    """
    Export PyTorch model to ONNX format
    
    Args:
        model_path: Path to trained PyTorch model
        output_path: Path to save ONNX model
        sequence_length: Input sequence length
    """
    print("Loading PyTorch model...")
    
    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = DroneTrajectoryLSTM(
        input_size=13,
        hidden_size=128,
        num_layers=2,
        output_size=6
    ).to(device)
    
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"Model loaded from {model_path}")
    print(f"Model architecture: {model}")
    
    # Create dummy input
    batch_size = 1
    dummy_input = torch.randn(batch_size, sequence_length, 13).to(device)
    
    print(f"\nExporting to ONNX...")
    print(f"Input shape: {dummy_input.shape}")
    
    # Export to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input_sequence'],
        output_names=['output', 'hidden_state'],
        dynamic_axes={
            'input_sequence': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print(f"Model successfully exported to {output_path}")
    
    # Verify the model
    print("\nVerifying ONNX model...")
    import onnx
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print("ONNX model is valid!")
    
    # Test inference
    print("\nTesting ONNX inference...")
    import onnxruntime as ort
    
    ort_session = ort.InferenceSession(output_path)
    
    # Run inference with dummy data
    dummy_input_np = dummy_input.cpu().numpy()
    outputs = ort_session.run(None, {'input_sequence': dummy_input_np})
    
    print(f"ONNX inference successful!")
    print(f"Output shape: {outputs[0].shape}")
    print(f"Sample output: {outputs[0][0]}")
    
    # Compare with PyTorch
    with torch.no_grad():
        torch_output, _ = model(dummy_input)
        torch_output_np = torch_output.cpu().numpy()
    
    diff = np.abs(torch_output_np - outputs[0]).max()
    print(f"\nMax difference between PyTorch and ONNX: {diff}")
    
    if diff < 1e-5:
        print("✓ ONNX model matches PyTorch model!")
    else:
        print("⚠ Warning: ONNX model differs from PyTorch model")
    
    # Save normalization parameters separately
    normalization = checkpoint['normalization']
    normalization_path = output_path.replace('.onnx', '_normalization.txt')
    
    with open(normalization_path, 'w') as f:
        f.write("# Normalization parameters for drone trajectory model\n")
        f.write("# Format: pos_mean_x pos_mean_y pos_mean_z pos_std_x pos_std_y pos_std_z\n")
        f.write("# vel_mean_x vel_mean_y vel_mean_z vel_std_x vel_std_y vel_std_z\n\n")
        
        pos_mean = normalization['pos_mean']
        pos_std = normalization['pos_std']
        vel_mean = normalization['vel_mean']
        vel_std = normalization['vel_std']
        
        f.write(f"pos_mean: {pos_mean[0]} {pos_mean[1]} {pos_mean[2]}\n")
        f.write(f"pos_std: {pos_std[0]} {pos_std[1]} {pos_std[2]}\n")
        f.write(f"vel_mean: {vel_mean[0]} {vel_mean[1]} {vel_mean[2]}\n")
        f.write(f"vel_std: {vel_std[0]} {vel_std[1]} {vel_std[2]}\n")
    
    print(f"\nNormalization parameters saved to {normalization_path}")
    
    print("\n" + "="*60)
    print("Export complete!")
    print("="*60)
    print(f"ONNX model: {output_path}")
    print(f"Normalization: {normalization_path}")
    print("\nYou can now use this model in C++ with ONNX Runtime")


if __name__ == '__main__':
    # Create models directory if it doesn't exist
    os.makedirs('../models', exist_ok=True)
    
    export_to_onnx(
        model_path='../models/best_model.pth',
        output_path='../models/drone_trajectory.onnx',
        sequence_length=10
    )
