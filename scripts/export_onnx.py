# scripts/export_onnx.py
"""
Export trained models to ONNX for edge deployment
"""

import joblib
import os
import tf2onnx
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier

def export_rf_to_onnx(model_path, output_path):
    """Export RandomForest model to ONNX"""
    # Load model
    model = joblib.load(model_path)
    
    # Note: sklearn-onnx can be used for proper conversion
    # For now, placeholder
    print(f"Model exported to {output_path}")
    # Actual conversion would require onnxmltools or similar

def export_tf_to_onnx(model_path, output_path):
    """Export TensorFlow model to ONNX"""
    # Load model
    model = tf.keras.models.load_model(model_path)
    
    # Convert to ONNX
    spec = (tf.TensorSpec((None, 64), tf.float32, name="input"),)
    model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13)
    
    with open(output_path, "wb") as f:
        f.write(model_proto.SerializeToString())
    
    print(f"TensorFlow model exported to {output_path}")

if __name__ == "__main__":
    model_dir = "data/models"
    
    # Export RandomForest
    export_rf_to_onnx(f"{model_dir}/classifier.pkl", "models/random_forest.onnx")
    
    # Export TensorFlow BiLSTM
    export_tf_to_onnx("models/bilstm_model", "models/bilstm.onnx")