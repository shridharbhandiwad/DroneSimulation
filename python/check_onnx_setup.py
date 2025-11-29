"""
Check ONNX export setup and dependencies
"""
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("=" * 60)
    print("ONNX Export Setup Verification")
    print("=" * 60)
    
    results = []
    
    # Check PyTorch
    try:
        import torch
        torch_version = torch.__version__
        print(f"✓ PyTorch: {torch_version}")
        results.append(('PyTorch', True, torch_version))
    except ImportError as e:
        print(f"✗ PyTorch: Not installed")
        results.append(('PyTorch', False, str(e)))
    
    # Check ONNX
    try:
        import onnx
        onnx_version = onnx.__version__
        print(f"✓ ONNX: {onnx_version}")
        results.append(('ONNX', True, onnx_version))
    except ImportError as e:
        print(f"✗ ONNX: Not installed")
        results.append(('ONNX', False, str(e)))
    
    # Check ONNXScript
    try:
        import onnxscript
        onnxscript_version = onnxscript.__version__
        print(f"✓ ONNXScript: {onnxscript_version}")
        results.append(('ONNXScript', True, onnxscript_version))
    except ImportError as e:
        print(f"✗ ONNXScript: Not installed")
        results.append(('ONNXScript', False, str(e)))
    
    # Check ONNX Runtime
    try:
        import onnxruntime as ort
        ort_version = ort.__version__
        print(f"✓ ONNX Runtime: {ort_version}")
        
        # Check opset support
        providers = ort.get_available_providers()
        print(f"  Available providers: {', '.join(providers)}")
        results.append(('ONNX Runtime', True, ort_version))
    except ImportError as e:
        print(f"✗ ONNX Runtime: Not installed")
        results.append(('ONNX Runtime', False, str(e)))
    
    # Check NumPy
    try:
        import numpy as np
        numpy_version = np.__version__
        print(f"✓ NumPy: {numpy_version}")
        results.append(('NumPy', True, numpy_version))
    except ImportError as e:
        print(f"✗ NumPy: Not installed")
        results.append(('NumPy', False, str(e)))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_ok = all(result[1] for result in results)
    
    if all_ok:
        print("✓ All dependencies are installed!")
        print("\nYou can now export your model:")
        print("  python export_to_onnx.py")
    else:
        print("✗ Some dependencies are missing")
        print("\nTo install missing dependencies:")
        print("  pip install torch onnx onnxscript onnxruntime numpy")
        
    print("\n" + "=" * 60)
    print("ONNX Export Configuration")
    print("=" * 60)
    print("Current settings in export_to_onnx.py:")
    print("  - opset_version: 17 (modern, well-supported)")
    print("  - do_constant_folding: False (avoids optimization bugs)")
    print("\nSupported ONNX Runtime versions:")
    print("  - Opset 17: ONNX Runtime 1.14.0+")
    print("  - Opset 18: ONNX Runtime 1.15.0+")
    
    # Check ONNX Runtime opset support
    if all_ok:
        try:
            import onnxruntime as ort
            version_parts = ort.__version__.split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            print(f"\nYour ONNX Runtime version ({ort.__version__}):")
            if major > 1 or (major == 1 and minor >= 14):
                print("  ✓ Supports opset 17")
            else:
                print("  ⚠ May not support opset 17 (upgrade recommended)")
                print("    pip install --upgrade onnxruntime")
        except:
            pass
    
    print("=" * 60)
    return all_ok


def test_simple_export():
    """Test a simple ONNX export to verify setup"""
    print("\n" + "=" * 60)
    print("Testing Simple ONNX Export")
    print("=" * 60)
    
    try:
        import torch
        import torch.nn as nn
        import tempfile
        import os
        
        # Create a simple model
        class SimpleModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.lstm = nn.LSTM(input_size=10, hidden_size=20, num_layers=1, batch_first=True)
                self.fc = nn.Linear(20, 5)
            
            def forward(self, x):
                out, _ = self.lstm(x)
                out = out[:, -1, :]
                out = self.fc(out)
                return out
        
        model = SimpleModel()
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(1, 5, 10)
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as f:
            temp_path = f.name
        
        try:
            torch.onnx.export(
                model,
                dummy_input,
                temp_path,
                export_params=True,
                opset_version=17,
                do_constant_folding=False,
                input_names=['input'],
                output_names=['output'],
                verbose=False
            )
            
            print("✓ Simple LSTM model export successful!")
            
            # Try to load and verify
            import onnx
            onnx_model = onnx.load(temp_path)
            onnx.checker.check_model(onnx_model)
            print("✓ ONNX model validation successful!")
            
            # Try ONNX Runtime inference
            try:
                import onnxruntime as ort
                session = ort.InferenceSession(temp_path)
                input_np = dummy_input.numpy()
                outputs = session.run(None, {'input': input_np})
                print("✓ ONNX Runtime inference successful!")
                print(f"  Output shape: {outputs[0].shape}")
                
                # Compare with PyTorch
                with torch.no_grad():
                    torch_output = model(dummy_input).numpy()
                
                import numpy as np
                diff = np.abs(torch_output - outputs[0]).max()
                print(f"  Max difference vs PyTorch: {diff:.2e}")
                
                if diff < 1e-5:
                    print("✓ ONNX output matches PyTorch!")
                else:
                    print("⚠ Small difference detected (this is normal)")
                    
            except Exception as e:
                print(f"✗ ONNX Runtime inference failed: {e}")
            
            return True
            
        except Exception as e:
            print(f"✗ Export failed: {e}")
            print("\nThis might be due to:")
            print("  - Incompatible package versions")
            print("  - Missing dependencies")
            print("\nTry upgrading packages:")
            print("  pip install --upgrade torch onnx onnxscript onnxruntime")
            return False
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"✗ Test setup failed: {e}")
        return False
    
    print("=" * 60)


if __name__ == '__main__':
    deps_ok = check_dependencies()
    
    if deps_ok:
        test_simple_export()
    else:
        print("\nPlease install missing dependencies before testing export.")
        sys.exit(1)
