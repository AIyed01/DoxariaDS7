import mlflow
import mlflow.tensorflow
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf
import os
import numpy as np

# Use a relative path for MLflow tracking that works in any environment
mlflow_tracking_dir = "./mlruns"
os.makedirs(mlflow_tracking_dir, exist_ok=True)
mlflow.set_tracking_uri(f"file://{os.path.abspath(mlflow_tracking_dir)}")

# Check for GPU availability
if tf.config.list_physical_devices('GPU'):
    print("GPU is available!")
else:
    print("GPU is not available!")

def build_model(input_shape=(224, 224, 3), num_classes=3):
    base_model = MobileNetV2(include_top=False, weights="imagenet", input_shape=input_shape)
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation="softmax")(x)
    model = Model(inputs=base_model.input, outputs=outputs)
    return model

def train_model(model, train_gen, val_gen, epochs=3):
    # Start MLflow run
    with mlflow.start_run() as run:
        print(f"MLflow Run ID: {run.info.run_id}")
        print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")
        print(f"MLflow Artifact URI: {mlflow.get_artifact_uri()}")
        
        # Log hyperparameters
        mlflow.log_param("epochs", epochs)
        mlflow.log_param("optimizer", "adam")
        mlflow.log_param("loss_function", "sparse_categorical_crossentropy")
        
        # Get sample data for model signature
        sample_images, _ = next(iter(train_gen))
        sample_input = sample_images[:1]  # Just take one sample
        
        # Check if sample_input is already a NumPy array
        if isinstance(sample_input, np.ndarray):
            input_example = sample_input  # It's already a NumPy array
        else:
            # Try to convert if it's a TensorFlow tensor
            input_example = sample_input.numpy()
        
        model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
        
        es = EarlyStopping(patience=3, restore_best_weights=True)
        
        # Train the model and log metrics
        history = model.fit(train_gen, validation_data=val_gen, epochs=epochs, callbacks=[es])
        
        # Log all metrics from history
        for epoch, (acc, val_acc, loss, val_loss) in enumerate(zip(
            history.history["accuracy"],
            history.history["val_accuracy"],
            history.history["loss"],
            history.history["val_loss"]
        )):
            mlflow.log_metrics({
                "accuracy": acc,
                "val_accuracy": val_acc,
                "loss": loss,
                "val_loss": val_loss
            }, step=epoch)
        
        # Log final metrics
        mlflow.log_metric("final_accuracy", history.history["accuracy"][-1])
        mlflow.log_metric("final_val_accuracy", history.history["val_accuracy"][-1])
        
        # Save model with Keras directly
        model_path = "model.keras"  # Use the new recommended format
        model.save(model_path)
        
        # Log the model with a signature
        signature = mlflow.models.infer_signature(
            input_example,
            model.predict(input_example)
        )
        
        # Log the model with proper signature and input example
        mlflow.tensorflow.log_model(
            model, 
            "tensorflow-model",
            signature=signature,
            input_example=input_example  # Use the properly handled input example
        )
        
        print("Model training and logging completed successfully")
        
        return model